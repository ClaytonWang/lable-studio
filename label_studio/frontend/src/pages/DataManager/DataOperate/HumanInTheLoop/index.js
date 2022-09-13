import {
  forwardRef,
  useCallback,
  useContext,
  useEffect,
  useImperativeHandle,
  useMemo,
  useRef,
  useState
} from "react";
import { Modal } from "@/components/Modal/Modal";
import { ApiContext } from '@/providers/ApiProvider';
import CreateEvaluate from "./CreateEvaluate";
import CreateTrain from "./CreateTrain";
import ModelAccuracy from "./ModelAccuracy";
import List from "./List";
import "./index.less";

export default forwardRef(({ project }, ref) => {
  const api = useContext(ApiContext);
  const modalRef = useRef();
  const [type, setType] = useState("list");
  const [modelId, setModelId] = useState('');
  const [evalId, setEvalId] = useState('');

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
    modalRef.current?.hide();
    setType("list");
  },[modalRef,setType]);

  const handler = useMemo(() => {
    return {
      onCancel: () => setType("list"),
      onTrain: () => setType("train"),
      onEvaluate: () => setType("evaluate"),
      onAccuracy: (eval_id,model_id) => {
        setModelId(model_id);
        setEvalId(eval_id);
        setType("accuracy");
      },
    };
  }, [setType]);

  return (
    <>
      <Modal
        bare
        ref={modalRef}
        className="human-zone"
        closeOnClickOutside={false}
        style={
          type === "evaluate" || type==="accuracy"
            ? {
              minWidth: 800,
            }
            : {
              width: "calc(100vw - 96px)",
              minWidth: 1000,
            }
        }
      >
        {type === "list" && <List onCancel={onCancel} onEvaluate={handler.onEvaluate} onTrain={handler.onTrain} onAccuracy={handler.onAccuracy } />}
        {type === "evaluate" && <CreateEvaluate onCancel={handler.onCancel} onSubmit={ onSubmit } />}
        {type === "train" && <CreateTrain onCancel={handler.onCancel} onSubmit={ onSubmit } />}
        {type === "accuracy" && <ModelAccuracy onCancel={handler.onCancel} modelId={ modelId } />}
      </Modal>
    </>
  );
});
