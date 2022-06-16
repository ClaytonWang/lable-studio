import { useEffect, useMemo, useRef, useState } from "react";
import { EditableProTable } from "@ant-design/pro-components";
import { Block, Elem } from "../../utils/bem";
import { Button } from "../../components/Button/Button";
import { Modal } from "../../components/Modal/Modal";
import { Space } from "../../components/Space/Space";
import { useAPI } from "../../providers/ApiProvider";
import { useProject } from "../../providers/ProjectProvider";

const PADDING = 32;

const formatResponse = (response) => {
  const { count, results } = response;

  return {
    data: results.map((item) => {
      const res = {
        id: item.id,
        origin: item.source ? JSON.stringify(item.source) : "",
        cleaning: item.algorithm ? JSON.stringify(item.algorithm) : "",
        _manual: item.manual ? JSON.stringify(item.manual) : "",
      };

      res.manual = res._manual || res.cleaning || res.origin || "";
      return res;
    }),
    success: true,
    total: count,
  };
};

export default ({ modalRef }) => {
  const api = useAPI();
  const { project } = useProject();
  const [status, setStatus] = useState({});
  const tableRef = useRef();

  const request = useMemo(() => {
    return {
      clExec: () => {
        return api.callApi("clExec", {
          body: {
            project_id: project.id,
          },
        });
      },
      clReplace: () => {
        const form = new FormData();

        form.append("project_id", project.id);
        return api.callApi("clReplace", {
          body: form,
        });
      },
      clList: (params) => {
        return api.callApi("clList", {
          params: {
            project_id: project.id,
            ...params,
          },
        });
      },
      clQueryStatus: () => {
        return api.callApi("clQueryStatus", {
          params: {
            project_id: project.id,
          },
        });
      },
      clLabelManually: (taskId, manual) => {
        const form = new FormData();

        form.append("manual", manual);
        return api.callApi("clLabelManually", {
          body: form,
          params: {
            id: taskId,
          },
        });
      },
    };
  }, [project.id]);

  useEffect(() => {
    const sync = () => {
      request.clQueryStatus().then((res) => {
        setStatus(res);
      });
    };

    sync();
    const timer = setInterval(sync, 3000);

    return clearInterval(timer);
  }, [request.clQueryStatus]);

  const handleExec = () => {
    request.clExec();
  };
  const handleReplace = () => {
    request.clReplace();
  };
  const handleRowDataChange = (id, data) => {
    request.clLabelManually(id, JSON.stringify(data.manual)).then(() => {
      tableRef?.current.reload();
    });
  };

  return (
    <Block name="cleandata">
      <Modal
        bare
        // visible
        ref={modalRef}
        style={{
          width: "calc(100vw - 96px)",
          minWidth: 1000,
          minHeight: 500,
          padding: PADDING,
        }}
      >
        <Elem name="wrapper">
          <Elem name="header">
            <Space>
              <Elem name="title">{t("clean_data_title", "数据清洗")}</Elem>
              <span>
                {status ? `${status.finish} / ${status.total}` : null}
              </span>
            </Space>
            <Space>
              <Elem name="buttons">
                <Button size="compact" onClick={() => modalRef?.current.hide()}>
                  {t("Cancel", "取消")}
                </Button>
              </Elem>
              <Elem name="buttons">
                <Space>
                  <Button size="compact" look="primary" onClick={handleExec}>
                    {t("clean_exec", "导入清洗算法")}
                  </Button>
                  <Button size="compact" look="primary" onClick={handleReplace}>
                    {t("clean_replace_data", "替换原对话")}
                  </Button>
                </Space>
              </Elem>
            </Space>
          </Elem>
          <Elem name="content">
            <EditableProTable
              rowKey="id"
              size="small"
              recordCreatorProps={false}
              scroll={{
                y: 500,
              }}
              pagination={{
                defaultPageSize: 30,
              }}
              actionRef={tableRef}
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
                },
                {
                  dataIndex: "manual",
                  title: t("manual_dialogue", "对话（人工修改）"),
                  valueType: "textarea",
                  render: (value, record) => {
                    return record._manual;
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
              request={({ pageSize, current }) => {
                return request
                  .clList({
                    page: current,
                    page_size: pageSize,
                  })
                  .then((res) => formatResponse(res));
              }}
            />
          </Elem>
        </Elem>
      </Modal>
    </Block>
  );
};
