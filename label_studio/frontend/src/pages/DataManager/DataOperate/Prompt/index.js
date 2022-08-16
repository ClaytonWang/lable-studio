import { forwardRef, useCallback, useEffect, useImperativeHandle, useMemo, useRef, useState } from "react";
import { Modal } from "@/components/Modal/Modal";
import { useAPI } from "@/providers/ApiProvider";
import { template } from '@/utils/util';
import ResponseGeneration from './ResponseGeneration';
import DialogIntent from './DialogIntent';
import './index.less';
import { message } from "antd";

const Prompt = forwardRef(({ project, showStatus }, ref) => {
  const modalRef = useRef();
  const api = useAPI();
  const [loading, setLoading] = useState(false);

  const request = useCallback(async (body = {}) => {
    setLoading(true);
    return api.callApi("mlPromptTemplateQuery", {
      params: { project: project.id },
    }).then(res => {
      if (res.templates?.length > 0) {
        return api.callApi('mlPromptPredict', {
          body: {
            project_id: project.id,
            ...body,
          },
        }).then(() => {
          setLoading(false);
          showStatus('prompt');
        });
      } else {
        setLoading(false);
        message.error(t('tip_please_complete'));
      }
    });
    
  }, [project, setLoading]);

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
    <Modal className="prompt-zone" bare ref={modalRef} style={{ width:800 }}>
      {
        Comp ? <Comp loading={loading} close={close} request={request} project={project} /> : null
      }
    </Modal>
  );
});

export default Prompt;
