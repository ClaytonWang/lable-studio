import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useHistory } from "react-router";
import { Form, Input, Button as AntButton } from "antd";
import { format } from "date-fns";
import { ProTable } from "@ant-design/pro-components";
import { get, values } from "lodash";
import { useContextProps } from "@/providers/RoutesProvider";
import { useAPI } from "@/providers/ApiProvider";
import { Button } from "@/components";
import { Space } from "@/components/Space/Space";
import { Modal } from "@/components/Modal/Modal";
import "./index.less";

export const ProjectCollection = () => {
  const setContextProps = useContextProps();
  const history = useHistory();
  const modalRef = useRef();
  const tableRef= useRef();
  const [form] = Form.useForm();
  const [status, setStatus] = useState();
  const [current, setCurrent] = useState();
  const api = useAPI();

  const back = useCallback(() => {
    history.push("/projects");
  }, []);
  const request = useMemo(() => {
    return {
      list: () => api.callApi("collections"),
      create: (body) =>
        api.callApi("createCollections", {
          body,
        }),
      update: (body) =>
        api.callApi("updateCollections", {
          body,
          params: {
            id: current.id,
          },
        }),
      delete: () =>
        api.callApi("deleteCollections", {
          params: {
            id: current.id,
          },
        }),
    };
  }, [current]);
  useEffect(() => {
    setContextProps({ back, create: () => setStatus("create") });
  }, []);
  useEffect(() => {
    if (status) {
      modalRef.current?.show();
    }
  }, [status]);
  const onFinish = useCallback(
    () => {
      if (!status) {
        return;
      }
      form.validateFields().then(values => {
        request[status]?.(values).then(() => {
          modalRef.current?.hide();
          tableRef.current?.reload();
        });
      });
    },
    [status, request]
  );
  const text = useMemo(() => {
    return {
      header: get(
        {
          create: t("Create Project Collection"),
          update: t("Edit Collection", "编辑集合"),
          delete: t("Delete Collection", "删除集合"),
        },
        status
      ),
      okButton: get(
        {
          delete: t("Delete Right Now", "立即删除"),
        },
        status,
        t("Confirm", "确定")
      ),
    };
  }, [status]);

  return (
    <div className="page-collections">
      <div style={{ padding: 20 }}>
        <ProTable
          actionRef={tableRef}
          columns={[
            {
              title: t("collection_name"),
              dataIndex: "title",
            },
            {
              title: t("created_at"),
              dataIndex: "created_at",
              render: (v) => format(new Date(v), "yyyy-MM-dd HH:mm:ss"),
            },
            {
              title: t("created_by"),
              dataIndex: "created_by",
            },
            {
              title: t("Operate", "操作"),
              render: (item) => {
                return (
                  <>
                    <AntButton
                      onClick={() => {
                        setStatus("update");
                        setCurrent(item);
                      }}
                      type="link"
                    >
                      {t("Edit")}
                    </AntButton>
                    <AntButton
                      onClick={() => {
                        setStatus("delete");
                        setCurrent(item);
                      }}
                      type="link"
                    >
                      {t("Delete")}
                    </AntButton>
                  </>
                );
              },
            },
          ]}
          request={() =>
            request.list().then((res) => {
              return {
                data: res.results,
                success: true,
              };
            })
          }
          toolBarRender={false}
          search={false}
          rowKey="id"
        />
      </div>
      <Modal
        className="collection-modal"
        bare
        ref={modalRef}
        style={{ width: 800 }}
        onHide={() => {
          setStatus(null);
          setCurrent(null);
        }}
      >
        <Form
          form={form}
          labelCol={{ span: 4 }}
          wrapperCol={{ span: 20 }}
          initialValues={current}
        >
          <Modal.Header>{text.header}</Modal.Header>
          <Form.Item
            label={t("collection_name", "集合名称")}
            name="title"
            rules={[
              {
                required: true,
                message: t("tip_please_complete", "请完整填写表单"),
              },
            ]}
          >
            <Input disabled={status === 'delete'} />
          </Form.Item>
          <Modal.Footer>
            <Space align="end">
              <Button onClick={() => modalRef.current?.hide()} size="compact">
                {t("Cancel")}
              </Button>
              <Button onClick={onFinish} size="compact" look="primary" type="submit">
                {text.okButton}
              </Button>
            </Space>
          </Modal.Footer>
        </Form>
      </Modal>
    </div>
  );
};
ProjectCollection.path = "/collections";
ProjectCollection.title = t("Project collection");
ProjectCollection.exact = true;
ProjectCollection.context = ({ back, create }) => {
  return (
    <Space>
      <Button onClick={back} size="compact">
        {t("Back", "返回")}
      </Button>
      <Button onClick={create} look="primary" size="compact">
        {t("Create Project Collection", "新增集合")}
      </Button>
    </Space>
  );
};
