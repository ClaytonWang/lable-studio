import { EditableProTable } from "@ant-design/pro-components";
import ReactDiffViewer from "react-diff-viewer";
import { Block, Elem } from "../../utils/bem";
import { Button } from "../../components/Button/Button";
import { Modal } from "../../components/Modal/Modal";
import { Space } from "../../components/Space/Space";

export default ({ modalRef }) => {
  const handleRowDataChange = (...params) => {
    console.log(params, "handleRowDataChange.params");
  };

  return (
    <Block name="cleandata">
      <Modal
        bare
        visible
        ref={modalRef}
        style={{
          width: "calc(100vw - 96px)",
          height: "calc(100vh - 96px)",
          minWidth: 1000,
          padding: 40,
        }}
      >
        <Elem name="wrapper">
          <Elem name="header">
            <Elem name="title">{t("clean_data_title", "数据清洗")}</Elem>
            <Space>
              <Elem name="buttons">
                <Button size="compact" onClick={() => modalRef?.current.hide()}>
                  {t("Cancel", "取消")}
                </Button>
              </Elem>
              <Elem name="buttons">
                <Button size="compact" look="primary">
                  {t("clean_data")}
                </Button>
              </Elem>
            </Space>
          </Elem>
          <Elem name="content">
            <EditableProTable
              rowKey="id"
              size="small"
              recordCreatorProps={false}
              editable={{
                type: "single",
                actionRender: (row, config, defaultDom) => [
                  defaultDom.save,
                  defaultDom.cancel,
                ],
                onSave: handleRowDataChange,
              }}
              columns={[
                {
                  width: 60,
                  dataIndex: "id",
                  title: "ID",
                  editable: false,
                },
                {
                  dataIndex: "origin",
                  title: t("origin_dialogue", "原对话"),
                  editable: false,
                },
                {
                  dataIndex: "cleaning",
                  title: t("cleaning_dialogue", "对话（清洗后）"),
                  editable: false,
                  render: (value, record) => {
                    const prev = record.origin;

                    if (!value || value === prev) {
                      return value;
                    }
                    return (
                      <ReactDiffViewer
                        oldValue={prev}
                        newValue={value}
                        splitView={false}
                        hideLineNumbers
                      />
                    );
                  },
                },
                {
                  dataIndex: "manual",
                  title: t("manual_dialogue", "对话（人工修改）"),
                  valueType: "textarea",
                  render: (value, record) => {
                    const prev = record.origin;

                    if (!value || value === prev) {
                      return value;
                    }
                    return (
                      <ReactDiffViewer
                        oldValue={prev}
                        newValue={value}
                        splitView={false}
                        hideLineNumbers
                      />
                    );
                  },
                },
                {
                  width: 100,
                  title: t("clean_manually", "人工修改"),
                  valueType: "option",
                  render: (text, record, _, action) => [
                    <a
                      key="editable"
                      onClick={() => {
                        action?.startEditable?.(record.id);
                      }}
                    >
                      {t("Edit", "编辑")}
                    </a>,
                  ],
                },
              ]}
              request={() => {
                return {
                  data: [
                    {
                      id: 1,
                      origin: "春花秋月何时了",
                      cleaning: "春花秋月何时了",
                      manual: "春花秋月何时了2",
                    },
                  ],
                };
              }}
            />
          </Elem>
        </Elem>
      </Modal>
    </Block>
  );
};
