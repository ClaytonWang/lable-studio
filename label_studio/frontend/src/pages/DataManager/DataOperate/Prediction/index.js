import { forwardRef, useCallback, useImperativeHandle, useMemo, useRef,useState } from "react";
import { Modal } from "@/components/Modal/Modal";
import { useAPI } from "@/providers/ApiProvider";
import { template } from '@/utils/util';
import ResponseGeneration from './ResponseGeneration';
import IntentResponse from './IntentResponse';
import './index.less';

const Prediction = forwardRef(({ project, showStatus }, ref) => {
  const modalRef = useRef();
  const api = useAPI();
  const [projectType,setProjectType] = useState(null);

  const request = useCallback(() => {
    return api.callApi('mlPredictProcess', {
      body: {
        project_id: project.id,
      },
    }).then(() => showStatus('prediction'));
  }, [project]);

  const onShow = useMemo(() => {
    const projectClass = template.class(project);

    switch (projectClass) {
      case 'intent-classification-for-dialog':
        setProjectType('intent');
        break;
      case 'conversational-ai-response-generation':
        setProjectType('response-generation');
        break;
    }
    return () => modalRef.current?.show();
  }, [project]);

  const close = useCallback(() => {
    modalRef.current?.hide();
  }, []);

  useImperativeHandle(ref, () => ({
    show: () => {
      onShow();
    },
  }));

  return (
    <Modal
      className="prediction-zone"
      bare
      ref={modalRef}
      style={{ width: 800 }}
      closeOnClickOutside={false}
      allowClose={true}
    >
      {
        projectType === 'intent' ? <IntentResponse close={close} execLabel={request} project={project} /> :
          (projectType === 'response-generation' ?
            <ResponseGeneration close={close} request={request} project={project} /> : null)}
    </Modal>
  );
});

export default Prediction;
