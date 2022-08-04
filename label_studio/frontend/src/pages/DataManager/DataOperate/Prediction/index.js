import {
  forwardRef,
  useCallback,
  useEffect,
  useImperativeHandle,
  useMemo,
  useRef,
  useState
} from "react";
import { get } from "lodash";
import { Modal } from "@/components/Modal/Modal";
import { useAPI } from "@/providers/ApiProvider";
import { template } from "@/utils/util";
import ResponseGeneration from "./ResponseGeneration";
import IntentResponse from "./IntentResponse";
import "./index.less";

const Prediction = forwardRef(({ project, showStatus }, ref) => {
  const modalRef = useRef();
  const api = useAPI();
  const [projectType, setProjectType] = useState(null);
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(false);

  const request = useCallback(
    (body) => {
      setLoading(true);
      return api
        .callApi("mlPredictProcess", {
          body: {
            project_id: project.id,
            ...body,
          },
        })
        .then(() => {
          setLoading(false);
          showStatus("prediction");
        });
    },
    [project, setLoading],
  );

  const onShow = useMemo(() => {
    const projectClass = template.class(project);
    const modelType = get(
      {
        "intent-classification-for-dialog": "intention",
        "conversational-ai-response-generation": "generation",
      },
      projectClass,
    );

    api
      .callApi("modelList", {
        params: {
          type: modelType,
        },
      })
      .then((res) => {
        setModels(res || []);
      });

    switch (projectClass) {
      case "intent-classification-for-dialog":
        setProjectType("intent");
        break;
      case "conversational-ai-response-generation":
        setProjectType("response-generation");
        break;
    }
    return () => modalRef.current?.show();
  }, [project]);

  const close = useCallback(() => {
    modalRef.current?.hide();
  }, []);

  // TEMP
  useEffect(() => {
    modalRef.current?.show();
  }),
  [];

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
      {projectType === "intent" ? (
        <IntentResponse close={close} loading={loading} execLabel={request} project={project} models={models} />
      ) : projectType === "response-generation" ? (
        <ResponseGeneration close={close} loading={loading} execLabel={request} project={project} models={models} />
      ) : null}
    </Modal>
  );
});

export default Prediction;
