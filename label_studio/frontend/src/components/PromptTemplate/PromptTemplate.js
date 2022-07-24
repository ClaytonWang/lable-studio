import { EditableProTable } from "@ant-design/pro-components";

const PromptTemplate = () => {

  const handleDataChange = () => {
  };
  const handleDelete = () => {
  };

  return (
    <>
      <EditableProTable
        rowKey="id"
        size="small"
        recordCreatorProps={false}
        scroll={{
          y: 500,
        }}
        style={{
          whiteSpace: "pre-wrap",
        }}
        pagination={{
          defaultPageSize: 30,
        }}
        editable={{
          type: "single",
          actionRender: (row, config, defaultDom) => [
            defaultDom.save,
            defaultDom.cancel,
          ],
        }}
        dataSource={[]}
        onDataSourceChange={handleDataChange}
        columns={[
          {
            width: 60,
            dataIndex: "id",
            title: "ID",
            editable: false,
          },
          {
            dataIndex: "data",
            title: "提示学习模版",
          },

          {
            width: 100,
            title: "操作",
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
              <a
                key="delete"
                onClick={handleDelete}
              >
              删除
              </a>,
            ],
          },
        ]}
      />
    </>
  );
};

export {
  PromptTemplate
};
