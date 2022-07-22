import { forwardRef, useCallback, useImperativeHandle, useMemo, useRef } from "react";
import { Modal } from "@/components/Modal/Modal";
import { useAPI } from "@/providers/ApiProvider";
import { template } from '@/utils/util';
import ResponseGeneration from './ResponseGeneration';
import DialogIntent from './DialogIntent';

const Prompt = forwardRef(({ project, showStatus }, ref) => {
  const modalRef = useRef();
  const api = useAPI();

  const request = useCallback(() => {
    return api.callApi('mlPromptPredict', {
      body: {
        project_id: project.id,
      },
    }).then(() => showStatus('prompt'));
  }, [project]);

  const Comp = useMemo(() => {
    const projectClass = template.class(project);

    switch (projectClass) {
      case 'intent-classification-for-dialog':
        return DialogIntent;
      case 'conversational-ai-response-generation':
        return ResponseGeneration;
    }
  }, [project]);

  const close = useCallback(() => {
    modalRef.current?.hide();
  }, []);

  useImperativeHandle(ref, () => ({
    show: () => {
      modalRef.current?.show();
    },
  }));

  return (
    <Modal bare ref={modalRef} style={{ width:800 }}>
      {
        Comp ? <Comp close={close} request={request} project={project} /> : null
      }
    </Modal>
  );
});

export default Prompt;
