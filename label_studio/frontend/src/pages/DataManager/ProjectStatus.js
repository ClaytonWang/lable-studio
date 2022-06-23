import { forwardRef, useEffect, useImperativeHandle, useMemo, useRef, useState } from "react";
import { Progress, Space } from 'antd';
import { find } from 'lodash';
import { useAPI } from "../../providers/ApiProvider";
import { useProject } from "../../providers/ProjectProvider";
import { Modal } from "../../components/Modal/Modal";

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

  const request = useMemo(() => {
    const fetchStatus = (type) => {
      return api.callApi("mlPreLabelProgress", {
        params: {
          project_id: project.id,
          type,
        },
      });
    };

    return async (fetchType) => {
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
    };
  }, [project.id]);

  useEffect(() => {
    if (task) {
      modalRef.current?.show();
      setVisible(true);
      const timer = setInterval(() => {
        request(task.type);
      }, 1000);
      
      return () => clearInterval(timer);
    } else {
      modalRef.current?.hide();
      if (visible) {
        // 进度结束后，刷新页面
        window.location.reload();
      }
    }
  }, [task?.state], visible);

  useEffect(() => {
    request();
  }, []);

  useImperativeHandle(ref, () => ({
    status: () => {
      request();
      setTimeout(request, 1000);
      setTimeout(request, 2000);
      setTimeout(request, 3000);
    },
  }));

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
            </Space>
          </div>
        ) : null
      }
    </Modal>
  );
});