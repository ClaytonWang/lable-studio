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
];

export default forwardRef((props, ref) => {
  const modalRef = useRef();
  const api = useAPI();
  const { project } = useProject();
  const [visible, setVisible] = useState(false);
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
        },
      });
    };

    return {
      cancelJob: async (jobType) => {
        return api.callApi("cancelJob", {
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
      },
    };
  }, [project.id]);

  useEffect(() => {
    if (task) {
      modalRef.current?.show();
      setVisible(task.type);
      const timer = setInterval(() => {
        request.sync(task.type);
      }, 3000);

      return () => clearInterval(timer);
    } else {
      if (visible) {
        // 进度结束后操作，默认刷新页面
        if (props.onFinish?.[visible]) {
          props.onFinish?.[visible]();
        } else {
          window.location.reload();
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
    status: () => {
      request.sync();
      setTimeout(request.sync, 1000);
      setTimeout(request.sync, 2000);
      setTimeout(request.sync, 3000);
    },
  }));

  const handleBack = useCallback(() => {
    history.push('/projects');
  }, []);

  const handleCancel = useCallback(() => {
    if (task?.type) {
      request.cancelJob(task?.type).then(() => {
        setTask(null);
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
              <h2>{t(`label_${task.type}`, task.type)}...</h2>
              <Progress type="circle" percent={progress} />
              <Space style={{ marginTop: 8 }}>
                {/* <Button onClick={handleCancel}>{t('Cancel')}</Button> */}
                <Button onClick={handleBack} look="primary">{t('back_pm_page', '返回项目管理页')}</Button>
              </Space>
            </Space>
          </div>
        ) : null
      }
    </Modal>
  );
});
