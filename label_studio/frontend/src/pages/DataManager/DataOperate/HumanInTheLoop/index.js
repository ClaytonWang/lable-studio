import {
  forwardRef,
  useCallback,
  useContext,
  useImperativeHandle,
  useRef
} from "react";
import { Modal } from "@/components/Modal/Modal";
import { ApiContext } from '@/providers/ApiProvider';
import CreateTrain from "./CreateTrain";
import "./index.less";

export default forwardRef(({ project,showStatus }, ref) => {
  const api = useContext(ApiContext);
  const modalRef = useRef();

  useImperativeHandle(ref, () => ({
    show: () => {
      modalRef.current?.show();
    },
  }));

  const onCancel = useCallback(() => {
    modalRef.current?.hide();
  }, [modalRef]);

  const onSubmit = useCallback(async (url,params) => {
    if (!url) return;
    await api.callApi(url, {
      body: {
        project_id: project.id,
        ...params,
      },
    });
    showStatus('train');
    modalRef.current?.hide();
  },[modalRef]);

  return (
    <>
      <Modal
        bare
        ref={modalRef}
        className="human-zone"
        closeOnClickOutside={false}
        style={
          {
            width: "calc(100vw - 96px)",
            minWidth: 1000,
          }
        }
      >
        <CreateTrain onCancel={onCancel} onSubmit={onSubmit} />
      </Modal>
    </>
  );
});
