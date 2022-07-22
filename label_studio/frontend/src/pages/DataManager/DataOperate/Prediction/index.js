import { forwardRef, useCallback, useImperativeHandle, useMemo, useRef } from "react";
import { Modal } from "@/components/Modal/Modal";
import { useAPI } from "@/providers/ApiProvider";
import { template } from '@/utils/util';
import ResponseGeneration from './ResponseGeneration';

const Prediction = forwardRef(({ project, showStatus }, ref) => {
  const modalRef = useRef();
  const api = useAPI();

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
        return request;
      case 'conversational-ai-response-generation':
        return () => modalRef.current?.show();
    }
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
    <Modal bare ref={modalRef}>
      <ResponseGeneration close={close} request={request} project={project} />
    </Modal>
  );
});

export default Prediction;
