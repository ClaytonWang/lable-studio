import { Modal } from "@/components/Modal/Modal";
import { Space } from "@/components/Space/Space";
import { Button } from "@/components/Button/Button";
import { PromptTemplate } from "@/components/PromptTemplate/PromptTemplate";

const ResponseGeneration = ({ close, project, request }) => {
  return (
    <>
      <Modal.Header>
        {t("label_prompt")}
      </Modal.Header>
      <PromptTemplate project={project} />
      <Modal.Footer>
        <Space align="end">
          <Button
            size="compact"
            onClick={close}
          >
            {t("Cancel")}
          </Button>
          <Button
            size="compact"
            look="primary"
            onClick={request}
          >
            {t("ceate_rightnow", "立即生成")}
          </Button>
        </Space>
      </Modal.Footer>
    </>
  );
};

export default ResponseGeneration;
