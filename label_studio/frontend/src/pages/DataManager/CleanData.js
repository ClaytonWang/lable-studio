import { forwardRef, useImperativeHandle, useMemo, useRef } from "react";
import { message } from 'antd';
import { EditableProTable } from "@ant-design/pro-components";
import { compact, trim } from "lodash";
import { Block, Elem } from "../../utils/bem";
import { Button } from "../../components/Button/Button";
import { Modal } from "../../components/Modal/Modal";
import { Space } from "../../components/Space/Space";
import { DiffChars } from "../../components/Diff";
import { useAPI } from "../../providers/ApiProvider";
import { useProject } from "../../providers/ProjectProvider";

const PADDING = 32;

const jsonToString = (value) => {
  try {
    if (value && typeof value === "object") {
      return value.map((item) => `${item.author}:${item.text||''}`).join("\n");
    }
  } catch (error) {
    return value;
  }
  return value;
};
const stringToJson = (string) => {
  return compact(
    trim(string)
      .split("\n")
      .map((item) => {
        const line = trim(item);
        const [author, text] = line.split(/:|：/);

        if (author || text) {
          return {
            author,
            text,
          };
        }
        return null;
      }),
  );
};

const formatResponse = (response) => {
  const { count, results } = response;

  return {
    data: results.map((item) => {
      const res = {
        id: item.id,
        origin: jsonToString(item.source),
        cleaning: jsonToString(item.algorithm),
        _manual: jsonToString(item.manual),
      };

      res.manual = res._manual || res.cleaning || res.origin || "";
      return res;
    }),
    success: true,
    total: count,
  };
};

export default forwardRef(({ showStatus }, ref) => {
  const api = useAPI();
  const { project } = useProject();
  const tableRef = useRef();
  const modalRef = useRef();

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
        return api.callApi("clReplace", {
          body: {
            project_id: project.id,
          },
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
        const manualData = (() => {
          try {
            return stringToJson(manual);
          } catch (error) {
            message.error(t('data_format_error', '数据格式错误'));
            throw(error);
          }
        })();

        return api.callApi("clLabelManually", {
          body: {
            manual: manualData,
          },
          params: {
            id: taskId,
          },
        });
      },
    };
  }, [project.id]);

  useImperativeHandle(ref, () => ({
    reload: () => {
      tableRef.current?.reload();
    },
    show: () => {
      modalRef.current?.show();
    },
  }));

  const handleExec = () => {
    request.clExec().then(showStatus);
  };
  const handleReplace = () => {
    request.clReplace();
  };
  const handleRowDataChange = (id, data) => {
    request.clLabelManually(id, data.manual).then(() => {
      tableRef?.current.reload();
    });
  };

  return (
    <Block name="cleandata">
      <Modal
        bare
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
              style={{
                whiteSpace: "pre-wrap",
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
                  render: (value, record) => {
                    if (value && value !== "-" && value !== record.origin) {
                      return (
                        <DiffChars oldValue={record.origin} newValue={value} />
                      );
                    }
                    return value || "-";
                  },
                },
                {
                  dataIndex: "manual",
                  title: t("manual_dialogue", "对话（人工修改）"),
                  valueType: "textarea",
                  render: (v, record) => {
                    const value = record._manual;

                    if (value && value !== "-" && value !== record.origin) {
                      return (
                        <DiffChars oldValue={record.origin} newValue={value} />
                      );
                    }
                    return value || "-";
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
});
