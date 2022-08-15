import {
  forwardRef,
  useCallback,
  useEffect,
  useImperativeHandle,
  useMemo,
  useRef,
  useState
} from "react";
import { Modal } from "@/components/Modal/Modal";
import CreateEvaluate from "./CreateEvaluate";
import CreateTrain from "./CreateTrain";
import List from "./List";
import "./index.less";

export default forwardRef(({ project }, ref) => {
  const modalRef = useRef();
  const [type, setType] = useState("list");

  useImperativeHandle(ref, () => ({
    show: () => {
      modalRef.current?.show();
    },
  }));

  const onCancel = useCallback(() => {
    modalRef.current?.hide();
  }, [modalRef]);
  const handler = useMemo(() => {
    return {
      onCancel: () => setType("list"),
      onTrain: () => setType("train"),
      onEvaluate: () => setType("evaluate"),
    };
  }, [setType]);

  // TEMP
  // useEffect(() => {
  //   modalRef.current?.show();
  //   setType("train");
  // }, []);

  console.log(type);

  return (
    <>
      <Modal
        bare
        ref={modalRef}
        className="human-zone"
        style={
          type === "evaluate"
            ? {
              minWidth: 800,
            }
            : {
              width: "calc(100vw - 96px)",
              minWidth: 1000,
            }
        }
      >
        {type === "list" && <List onCancel={onCancel} onEvaluate={handler.onEvaluate} onTrain={handler.onTrain} />}
        {type === "evaluate" && <CreateEvaluate onCancel={handler.onCancel} />}
        {type === "train" && <CreateTrain onCancel={handler.onCancel} />}
      </Modal>
    </>
  );
});
