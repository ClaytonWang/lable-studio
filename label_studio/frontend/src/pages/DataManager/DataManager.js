import React,{ createRef, useCallback, useEffect, useRef,useState } from 'react';
import { generatePath, useHistory } from 'react-router';
import { NavLink } from 'react-router-dom';
import { Loading } from '../../components';
import { Button } from '../../components/Button/Button';
import { modal, Modal } from '../../components/Modal/Modal';
import { Space } from '../../components/Space/Space';
import { useAPI } from '../../providers/ApiProvider';
import { useLibrary } from '../../providers/LibraryProvider';
import { useProject } from '../../providers/ProjectProvider';
import { useContextProps, useFixedLocation, useParams } from '../../providers/RoutesProvider';
import { addAction, addCrumb, deleteAction, deleteCrumb } from '../../services/breadrumbs';
import { Block, Elem } from '../../utils/bem';
import { isDefined } from '../../utils/helpers';
import { ImportModal } from '../CreateProject/Import/ImportModal';
import { ExportPage } from '../ExportPage/ExportPage';
import { APIConfig } from './api-config';
import CleanData from './CleanData';
import { Progress } from 'antd';
import { PromptLearnTemplate } from '../../components';
import "./DataManager.styl";

const refModal = createRef();
const refProm = createRef();

const onPreButtonClick = (e,params) => {
  const mlQueryProgress = params.mlQueryProgress;
  const setProgress = params.setProgress;
  const mlPredictProcess = params.mlPredictProcess;

  mlPredictProcess();

  let progress = 0,count=0;

  refModal.current?.show();
  let t = setInterval(() => {
    count = count + 1;
    mlQueryProgress().then((rst) => {
      progress = rst.rate * 100;
      setProgress(progress);

      if (progress >= 100 || (progress === 0 && count > 11)) {
        clearInterval(t);
        setProgress(0);
        try { refModal.current?.hide(); } catch (e) { console.log(e); }
        return;
      }
    });
  },1000);
};

const onPrePromButtonClick = () => {
  refProm.current?.show();
};

const initializeDataManager = async (root, props, params) => {
  if (!window.LabelStudio) throw Error("Label Studio Frontend doesn't exist on the page");
  if (!root && root.dataset.dmInitialized) return;

  root.dataset.dmInitialized = true;

  const { ...settings } = root.dataset;

  const dmConfig = {
    root,
    toolbar: "actions columns filters ordering wash-button pre-button pre-prom-button label-button loading-possum error-box  | refresh import-button export-button view-toggle",
    projectId: params.id,
    apiGateway: `${window.APP_SETTINGS.hostname}/api/dm`,
    // apiGateway: `http://124.71.161.146:8080/api/dm`,
    apiVersion: 2,
    project: params.project,
    polling: !window.APP_SETTINGS,
    showPreviews: true,
    apiEndpoints: APIConfig.endpoints,
    apiHeaders: {
      Authorization: `Token c1b81ee6d2f3e278aca0b4707f109f4d20facbf6`,
    },
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
      'wash-button': () => {
        return () => <button className="dm-button dm-button_size_medium dm-button_look_primary" onClick={params.handleClickClear} >{t("clean_data", "清洗")}</button>;
      },
      'pre-button': () => {
        return () => <button className="dm-button dm-button_size_medium dm-button_look_primary" onClick={(e) => { onPreButtonClick(e,params);}} >预标注(普通)</button>;
      },
      'pre-prom-button': () => {
        return () => <button className="dm-button dm-button_size_medium dm-button_look_primary" onClick={(e) => { onPrePromButtonClick(e,params);}} >预标注(提示学习)</button>;
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
  const [progress, setProgress] = useState(0);
  const clearModalRef = useRef();
  const dataManagerRef = useRef();
  const projectId = project?.id;

  const mlPredictProcess = useCallback(async () => {
    return await api.callApi('mlPredictProcess', {
      body: {
        project_id: project.id,
      },
    });
  }, [project]);

  const mlQueryProgress = useCallback(async () => {
    return await api.callApi('mlPreLabelProgress', {
      params: { project_id: project.id },
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
        autoAnnotation: isDefined(interactiveBacked),
        setProgress,
        mlQueryProgress,
        mlPredictProcess,
        handleClickClear: () => clearModalRef?.current.show(),
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
      <Elem name="info">Project was deleted or not yet created</Elem>

      <Button to="/projects">
        Back to projects
      </Button>
    </Block>
  ) : (
    <>
      <PromptLearnTemplate ref={refProm} projectId={projectId} />
      <Modal
        ref={refModal}
        bare={true}
        allowClose={false}
        animateAppearance={false}
        onHide={
          async () => {
            await dataManagerRef?.current?.store?.fetchProject({ force: true, interaction: 'refresh' });
            await dataManagerRef?.current?.store?.currentView?.reload();
          }
        }
        style={{
          width: '150px',
          minWidth:'150px',
          background: 'transparent',
          boxShadow: 'none' }}
      >
        <Progress type="circle" percent={progress} format={percent => `标注中${percent.toFixed(0)}%`}  />
      </Modal>
      <CleanData
        modalRef={clearModalRef}
      />
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
      addCrumb({
        key: "dm-crumb",
        // title: "Labeling",
        title:"(对话-意图分类)",
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
