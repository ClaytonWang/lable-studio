import { useEffect, useMemo,useRef,useState } from 'react';
import { Input, message, Select, Space, Tag, Tooltip } from 'antd';
import { get, startsWith } from 'lodash';
import { EditableProTable } from "@ant-design/pro-components";
import { PlusOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import { useAPI } from "@/providers/ApiProvider";
import "./PromptTemplate.less";

const PromptTemplate = ({ project }) => {
  const actionRef = useRef();
  const api = useAPI();
  const [labelOptions, setLabelOptions] = useState([]);

  const request = useMemo(() => {
    return {
      list: () => {
        return api.callApi("mlPromptTemplateQuery", {
          params: { project: project.id },
        }).then(res => {
          return {
            data: res.templates,
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
            success:true,
          };

        });
      },
      create: ({ template,label }) => {
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
      update: (id, template,label) => {
        return api.callApi("mlPromptTemplateUpdate", {
          params: { id },
          body: { template ,label },
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
        request.create({ template:data.template, label:data.tags.join('|||') }).then(() => {
          actionRef.current?.reload();
        });
      } else {
        request.update(data.id, data.template, data.tags.join('|||')).then(() => {
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
        columns={[
          {
            dataIndex: "template",
            width:"60%",
            title: <Space>
              <span>{t('prompt_template', "提示学习模版")}</span>
              <Tooltip title={t('tip_prompt_template', "[dlg]代表整个对话，[dlg1]代表对话第一行，[dlg2]代表对话第二行，[dlgx]代表对话第x行，[mask]代表被遮罩的内容。")} overlayInnerStyle={{ borderRadius: 5 }}>
                <QuestionCircleOutlined />
              </Tooltip>
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
          },
          {
            dataIndex: "tags",
            title: "标签",
            width:"40%",
            renderFormItem: (_, { isEditable , record }) =>{
              return isEditable ? (
                <Select
                  mode="multiple"
                  allowClear
                  style={{
                    width: '100%',
                    marginTop:5,
                  }}
                  placeholder="请选择标签"
                  options={labelOptions}
                />
              ) : record.tags?.map(i => {
                return <Tag key={i}>{i}</Tag>;
              });
            },
            formItemProps: {
              rules: [
                {
                  required: true,
                  message: t("tip_please_complete"),
                },
              ],
            },
          },
          {
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
          },
        ]}
      />
    </div>
  );
};

export {
  PromptTemplate
};
