import { forwardRef, useCallback, useEffect, useImperativeHandle, useMemo, useRef, useState } from "react";
import { useHistory } from 'react-router';
import { Progress, Space } from 'antd';
import { find } from 'lodash';
import { useAPI } from "../../providers/ApiProvider";
import { useProject } from "../../providers/ProjectProvider";
import { Modal } from "../../components/Modal/Modal";
import { Button } from '../../components';

const TASK_TYPE = [
  'prediction',
  'clean',
  'prompt',
  'train',
];

const dataReload = () => {
  window.dataManager.store.fetchProject({ force: true, interaction: 'refresh' });
  window.dataManager.store.currentView?.reload();
};

export default forwardRef((props, ref) => {
  const modalRef = useRef();
  const api = useAPI();
  const { project } = useProject();
  const [visible, setVisible] = useState(false);
  const [loading, setLoading] = useState(false);
  const [task, setTask] = useState(null);
  const history = useHistory();

  const request = useMemo(() => {
    const fetchStatus = (type) => {
      if (!project.id) {
        return {};
      }

      return api.callApi("mlPreLabelProgress", {
        params: {
          project_id: project.id,
          type,
          category: type === 'train' ? 'train' : 'model',
        },
      });
    };

    return {
      cancelJob: async (jobType) => {
        return await api.callApi("cancelJob", {
          params: {
            project_id: project.id,
            type: jobType,
          },
        });
      },
      sync: async (fetchType) => {
        const tasks = fetchType ? [fetchType] : TASK_TYPE;
        const list = await Promise.all(tasks.map(async item => {
          const data = await fetchStatus(item);

          return {
            ...data,
            type: item,
            state: data.state === 6 || data.state === 3,
          };
        }));
        const running = find(list, { state: true });

        if (running) {
          setTask({
            ...running,
          });
        } else {
          setTask(null);
        }
        return running;
      },
    };
  }, [project.id]);

  useEffect(() => {
    if (task) {
      modalRef.current?.show();
      setVisible(task.type);
      const timer = setInterval(() => {
        request.sync(task.type);
      }, 2000);

      return () => clearInterval(timer);
    } else {
      if (visible) {
        // 进度结束后操作，默认刷新页面
        if (props.onFinish?.[visible]) {
          props.onFinish?.[visible]();
        } else {
          dataReload();
        }

        modalRef.current?.hide();
        setVisible(null);
      }
    }
  }, [task?.state, visible]);

  useEffect(() => {
    request.sync();
  }, []);

  useImperativeHandle(ref, () => ({
    status: (taskType) => {
      request.sync().then(res => {
        if (TASK_TYPE.includes(taskType) && res?.state !== true) {
          if (props.onFinish?.[taskType]) {
            props.onFinish?.[taskType]();
          } else {
            dataReload();
          }
        }
      });
    },
  }));

  const handleBack = useCallback(() => {
    history.push('/projects');
  }, []);

  const handleCancel = useCallback(() => {
    if (task?.type) {
      setLoading(true);
      request.cancelJob(task.type).then(() => {
        setTask(null);
        setLoading(false);
        if (props.onCancel?.[task.type]) {
          props.onCancel?.[task.type]();
        }
      });
    }
  }, [task?.type]);

  const progress = useMemo(() => {
    if (task?.rate) {
      return (task.rate * 100).toFixed(0);
    }
    return 0;
  }, [task?.rate]);

  return (
    <Modal
      ref={modalRef}
      bare
      allowClose={false}
      animateAppearance={false}
    >
      {
        task ? (
          <div style={{ padding: 16, textAlign: 'center' }}>
            <Space direction="vertical">
              <h2>{t.format('with_template', `label_${task.type}`, task.type)}...</h2>
              <Progress strokeColor={{
                '0%': '#108ee9',
                '100%': '#87d068',
              }} type="circle" percent={progress} />
              <Space style={{ marginTop: 8 }}>
                {
                  task.type === "train" ? null : <Button waiting={loading} onClick={handleCancel}>{t('Cancel')}</Button>
                }
                <Button style={{ marginLeft: 24 }} onClick={handleBack} look="primary">{t('back_pm_page', '返回项目管理页')}</Button>
              </Space>
            </Space>
          </div>
        ) : null
      }
    </Modal>
  );
});
