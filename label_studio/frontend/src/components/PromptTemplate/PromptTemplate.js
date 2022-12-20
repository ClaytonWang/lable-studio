import { useEffect, useMemo, useRef,useState } from 'react';
import { Input, message, Select, Space, Tag, Tooltip } from 'antd';
import { get, startsWith } from 'lodash';
import { EditableProTable } from "@ant-design/pro-components";
import { PlusOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import { useAPI } from "@/providers/ApiProvider";
import "./PromptTemplate.less";

const PromptTemplate = ({ project, tag }) => {
  const actionRef = useRef();
  const api = useAPI();
  const [labelOptions, setLabelOptions] = useState([]);

  const request = useMemo(() => {
    return {
      list: () => {
        return api.callApi("mlPromptTemplateQuery", {
          params: { project: project.id },
        }).then(res => {
          const templates = res.templates.map(i => {
            return { ...i, label: i.label?.split('|||') };
          });

          return {
            data: templates,
            success: true,
          };
        });
      },
      labels: () => {
        return api.callApi("mlProjectLabels", {
          params: { pk: project.id },
        }).then(res => {
          return {
            data: res || [],
            success: true,
          };

        });
      },
      create: ({ template, label }) => {
        return api.callApi("mlPromptTemplateCreate", {
          params: { id: project.id },
          body: {
            project: project.id,
            template,
            label,
          },
          errorFilter: (res) => {
            const error = startsWith(res.error, 'duplicate') ? '提示学习模板已存在，请重新输入' : res.error;

            message.error(error);
          },
        });
      },
      delete: (id) => {
        return api.callApi("mlPromptTemplateDelete", {
          body: { id },
        });
      },
      update: (id, template, label) => {
        return api.callApi("mlPromptTemplateUpdate", {
          params: { id },
          body: { template, label },
          errorFilter: (res) => {
            const error = startsWith(get(res, 'response.error', res.error), 'duplicate') ? '提示学习模板已存在，请重新输入' : res.error;

            message.error(error);
          },
        });
      },
    };
  }, [project]);

  const handleSave = (key, data) => {
    if (data.template) {
      if (data.type === 'add') {
        request.create({ template: data.template, label: data.label? data.label.join('|||'):'' }).then(() => {
          actionRef.current?.reload();
        });
      } else {
        request.update(data.id, data.template, data.label? data.label.join('|||'):'').then(() => {
          actionRef.current?.reload();
        });
      }
    }
  };

  const handleDelete = (id) => {
    request.delete(id).then(() => {
      actionRef.current?.reload();
    });
  };

  useEffect(() => {
    const options = [];

    request.labels().then(res => {
      res.data?.forEach(i => {
        options.push({
          label: i,
          value: i,
        });
      });
      setLabelOptions(options);
    });
  }, []);

  const tblcolumns = useMemo(() => {
    const rslt = [{
      dataIndex: "template",
      width: tag ? "60%" : "80%",
      title: <Space>
        <span>{t('prompt_template', "提示学习模版")}</span>
      </Space>,
      renderFormItem: (_, { isEditable }) => {
        return isEditable ? (
          <Input.TextArea placeholder={t("help_prompt_template", "请输入提示学习模板,例:[dlg]你的心情很[mask]")} />
        ) : <span />;
      },
      formItemProps: {
        rules: [
          {
            required: true,
            message: t("tip_please_complete"),
          },
        ],
      },
    }];

    if (tag) {
      rslt.push({
        dataIndex: "label",
        title: "标签",
        width: "40%",
        renderFormItem: (_, { isEditable }) => {
          return isEditable ? (
            <Select
              mode="multiple"
              allowClear
              style={{
                width: '100%',
                marginTop: 5,
              }}
              placeholder="请选择标签"
              options={labelOptions}
            />
          ) : <span />;
        },
        render: (_, row) => {
          return row?.label?.map((item) => <Tag key={item}>{item}</Tag>);
        },
        formItemProps: {
          rules: [
            {
              required: true,
              message: t("tip_please_complete"),
            },
          ],
        },
      });
    }
    rslt.push({
      width: 100,
      title: t("Operate"),
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
          onClick={() => handleDelete(record.id)}
        >
          {t("Delete")}
        </a>,
      ],
    });
    return rslt;
  }, [tag,labelOptions]);

  return (
    <div className='prompt-template'>
      <div className='operate-zone'>
        <Space align="end">
          <a
            size='small'
            type="primary"
            onClick={() => {
              actionRef.current?.addEditRecord?.({
                id: Date.now(),
                type: 'add',
              });
            }}
          // icon={<PlusOutlined />}
          >{t("Insert")}<PlusOutlined /></a>
        </Space>
      </div>
      <EditableProTable
        actionRef={actionRef}
        rowKey="id"
        recordCreatorProps={false}
        scroll={{
          y: 500,
        }}
        style={{
          whiteSpace: "pre-wrap",
          marginLeft: tag ? 0 : 20,
        }}
        request={request.list}
        pagination={false}
        editable={{
          type: "multiple",
          actionRender: (row, config, defaultDom) => [
            defaultDom.save,
            defaultDom.cancel,
          ],
          onSave: handleSave,
        }}
        dataSource={[]}
        columns={tblcolumns}
      />
    </div>
  );
};

export {
  PromptTemplate
};
