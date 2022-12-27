import React,{ createRef, useCallback, useEffect, useMemo,useRef, useState } from 'react';
import { generatePath, useHistory } from 'react-router';
import { NavLink } from 'react-router-dom';
import { Loading } from '../../components';
import { Button } from '../../components/Button/Button';
import { modal } from '../../components/Modal/Modal';
import { Space } from '../../components/Space/Space';
import { useAPI } from '../../providers/ApiProvider';
import { useLibrary } from '../../providers/LibraryProvider';
import { useProject } from '../../providers/ProjectProvider';
import { useContextProps, useFixedLocation, useParams } from '../../providers/RoutesProvider';
import { addAction, deleteAction, deleteCrumb } from '../../services/breadrumbs';
import { Block, Elem } from '../../utils/bem';
import { isDefined } from '../../utils/helpers';
import { ImportModal } from '../CreateProject/Import/ImportModal';
import { ExportPage } from '../ExportPage/ExportPage';
import { APIConfig } from './api-config';
import { useConfig } from "@/providers/ConfigProvider";
import ProjectStatus from './ProjectStatus';
import DataOperate, { Clean, HumanInTheLoop, Prediction, Prompt } from './DataOperate';
import { CleanConfig } from "./DataOperate/Clean/CleanConfig";
import { template } from '@/utils/util';
import "./DataManager.styl";

// 按钮相关操作
const { refs, showStatus, actions } = (() => {
  const refs = {
    status: createRef(),
    cleanCfg: createRef(),
    clean: createRef(),
    prompt: createRef(),
    prediction: createRef(),
    human: createRef(),
  };
  const showStatus = (type) => refs.status.current?.status(type);
  const actions = {
    cleanCfg: () => refs.cleanCfg.current?.show(),
    clean: () => refs.clean.current?.show(),
    prompt: () => refs.prompt.current?.show(),
    prediction: () => refs.prediction.current?.show(),
    human: () => refs.human.current?.show(),
  };

  return { refs, actions, showStatus };
})();

const initializeDataManager = async (root, props, params) => {
  if (!window.LabelStudio) throw Error("Label Studio Frontend doesn't exist on the page");
  if (!root && root.dataset.dmInitialized) return;

  root.dataset.dmInitialized = true;

  const { ...settings } = root.dataset;

  const dmConfig = {
    root,
    toolbar: "actions columns filters ordering operate label-button loading-possum error-box  | refresh import-button export-button view-toggle",
    projectId: params.id,
    apiGateway: `${window.APP_SETTINGS.hostname}/api/dm`,
    apiVersion: 2,
    project: params.project,
    polling: !window.APP_SETTINGS,
    showPreviews: true,
    apiEndpoints: APIConfig.endpoints,
    interfaces: {
      backButton: false,
      labelingHeader: false,
      groundTruth: false,
      instruction: false,
      autoAnnotation: params.autoAnnotation,
    },
    labelStudio: {
      keymap: window.APP_SETTINGS.editor_keymap,
    },
    instruments: {
      // 自定义按钮
      'operate': () => (props) => {
        const { store } = props;
        const hasData = (store.project?.task_count ?? store.project?.task_number ?? 0) > 0;

        if (!hasData) return null;
        return (
          <DataOperate
            project={params.project}
            actions={params.actions}
          />
        );
      },
    },
    ...props,
    ...settings,
  };

  return new window.DataManager(dmConfig);
};

const buildLink = (path, params) => {
  return generatePath(`/projects/:id${path}`, params);
};

export const DataManagerPage = ({ ...props }) => {
  const root = useRef();
  const params = useParams();
  const history = useHistory();
  const api = useAPI();
  const { project } = useProject();
  const LabelStudio = useLibrary('lsf');
  const DataManager = useLibrary('dm');
  const setContextProps = useContextProps();
  const [crashed, setCrashed] = useState(false);
  const dataManagerRef = useRef();
  const projectId = project?.id;

  const mlPredictProcess = useCallback(async () => {
    return await api.callApi('mlPredictProcess', {
      body: {
        project_id: project.id,
      },
    });
  }, [project]);

  const init = useCallback(async () => {
    if (!LabelStudio) return;
    if (!DataManager) return;
    if (!root.current) return;
    if (!project?.id) return;
    if (dataManagerRef.current) return;

    const mlBackends = await api.callApi("mlBackends", {
      params: { project: project.id },
    });
    const interactiveBacked = (mlBackends ?? []).find(({ is_interactive }) => is_interactive);

    const dataManager = (dataManagerRef.current = dataManagerRef.current ?? await initializeDataManager(
      root.current,
      props,
      {
        ...params,
        project,
        actions,
        autoAnnotation: isDefined(interactiveBacked),
        mlPredictProcess,
      },
    ));

    Object.assign(window, { dataManager });

    dataManager.on("crash", () => setCrashed());

    dataManager.on("settingsClicked", () => {
      history.push(buildLink("/settings/labeling", { id: params.id }));
    });

    dataManager.on("importClicked", () => {
      history.push(buildLink("/data/import", { id: params.id }));
    });

    dataManager.on("exportClicked", () => {
      history.push(buildLink("/data/export", { id: params.id }));
    });

    dataManager.on("error", response => {
      api.handleError(response);
    });

    if (interactiveBacked) {
      dataManager.on("lsf:regionFinishedDrawing", (reg, group) => {
        const { lsf, task, currentAnnotation: annotation } = dataManager.lsf;
        const ids = group.map(r => r.id);
        const result = annotation.serializeAnnotation().filter((res) => ids.includes(res.id));

        const suggestionsRequest = api.callApi("mlInteractive", {
          params: { pk: interactiveBacked.id },
          body: {
            task: task.id,
            context: { result },
          },
        });

        lsf.loadSuggestions(suggestionsRequest, (response) => {
          if (response.data) {
            return response.data.result;
          }

          return [];
        });
      });
    }

    setContextProps({ dmRef: dataManager });
  }, [LabelStudio, DataManager, projectId]);

  const destroyDM = useCallback(() => {
    if (dataManagerRef.current) {
      dataManagerRef.current.destroy();
      dataManagerRef.current = null;
    }
  }, [dataManagerRef]);

  useEffect(() => {
    init();

    return () => destroyDM();
  }, [root, init]);

  if (!DataManager || !LabelStudio) {
    return (
      <div style={{
        flex: 1,
        width: '100%',
        height: '100%',
        display: "flex",
        alignItems: 'center',
        justifyContent: 'center',
      }}>
        <Loading size={64}/>
      </div>
    );
  }

  return crashed ? (
    <Block name="crash">
      <Elem name="info">{t('tip_deleted_not_created')}</Elem>

      <Button to="/projects">
        {t('Back to projects')}
      </Button>
    </Block>
  ) : (
    <>
      <Prediction ref={refs.prediction} project={project} showStatus={showStatus} />
      <Prompt ref={refs.prompt} project={project} showStatus={showStatus} />
      <Clean ref={refs.clean} showStatus={showStatus} />
      <CleanConfig ref={refs.cleanCfg} cleanRefs={ refs.clean} />
      <ProjectStatus ref={refs.status}
        onFinish={{
          clean: () => refs.clean.current?.reload(),
        }}
        onCancel={{
          clean: () => refs.clean.current?.reload(),
        }}
      />
      <HumanInTheLoop ref={refs.human} showStatus={showStatus} project={project} />
      <Block ref={root} name="datamanager"/>
    </>

  );
};

DataManagerPage.path = "/data";
DataManagerPage.pages = {
  ExportPage,
  ImportModal,
};
DataManagerPage.context = ({ dmRef }) => {
  const location = useFixedLocation();
  const { project } = useProject();
  const [mode, setMode] = useState(dmRef?.mode ?? "explorer");

  const links = {
    '/settings': t("Settings"),
  };

  const updateCrumbs = (currentMode) => {
    const isExplorer = currentMode === 'explorer';
    const dmPath = location.pathname.replace(DataManagerPage.path, '');

    if (isExplorer) {
      deleteAction(dmPath);
      deleteCrumb('dm-crumb');
    } else {
      addAction(dmPath, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dmRef?.store?.closeLabeling?.();
      });
    }
  };

  const showLabelingInstruction = (currentMode) => {
    const isLabelStream = currentMode === 'labelstream';
    const { expert_instruction, show_instruction } = project;

    if (isLabelStream && show_instruction && expert_instruction) {
      modal({
        title: t("Labeling Instructions"),
        body: <div dangerouslySetInnerHTML={{ __html: expert_instruction }}/>,
        style: { width: 680 },
      });
    }
  };

  const onDMModeChanged = (currentMode) => {
    setMode(currentMode);
    updateCrumbs(currentMode);
    showLabelingInstruction(currentMode);
  };

  useEffect(() => {
    if (dmRef) {
      dmRef.on('modeChanged', onDMModeChanged);
    }

    return () => {
      dmRef?.off?.('modeChanged', onDMModeChanged);
    };
  }, [dmRef, project]);

  const isShowCycl = project.show_cycle_human_btn && ((project?.task_count ?? project?.task_number ?? 0) > 0);


  return project && project.id ? (
    <Space size="small">
      {(project.expert_instruction && mode !== 'explorer') && (
        <Button size="compact" onClick={() => {
          modal({
            title: t("Instructions"),
            body: () => <div dangerouslySetInnerHTML={{ __html: project.expert_instruction }}/>,
          });
        }}>
          {t("Instructions")}
        </Button>
      )}

      {
        isShowCycl ? (
          <Button
            size="compact"
            data-external
            onClick={actions.human}
          >
            {t('on_the_road', '人在环路')}
          </Button>
        ) : null
      }

      {Object.entries(links).map(([path, label]) => (
        <Button
          key={path}
          tag={NavLink}
          size="compact"
          to={`/projects/${project.id}${path}`}
          data-external
        >
          {label}
        </Button>
      ))}
    </Space>
  ) : null;
};
