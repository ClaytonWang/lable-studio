import { forwardRef, useEffect, useImperativeHandle, useMemo, useRef } from "react";
import { Modal } from "@/components/Modal/Modal";
import "./index.less";

const formItemLayout = {
  labelCol: { span: 4 },
  wrapperCol: { span: 20 },
};

export default forwardRef(({ project }, ref) => {
  const modalRef = useRef();

  useImperativeHandle(ref, () => ({
    show: () => {
      modalRef.current?.show();
    },
  }));

  // TEMP
  // useEffect(() => {
  //   modalRef.current?.show();
  // }, []);

  return (
    <Modal
      bare
      ref={modalRef}
      className="human-zone"
      style={{
        width: "calc(100vw - 96px)",
        minWidth: 1000,
        minHeight: 500,
      }}
    >
      <Modal.Header>对话生成(0样本)</Modal.Header>
    </Modal>
  );
});
