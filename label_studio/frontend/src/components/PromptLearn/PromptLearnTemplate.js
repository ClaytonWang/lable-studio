import { Button, Form, Input, Popconfirm, Table, Tooltip, Typography } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import React, { useCallback ,useImperativeHandle,useState } from 'react';
import { FaQuestionCircle } from "react-icons/fa";
import { Modal } from '../../components/Modal/Modal';
import { Icon } from "../Icon/Icon";
import { Space } from "../Space/Space";
import { useAPI } from '../../providers/ApiProvider';
import './PromptLearnTemplate.css';

const { TextArea } = Input;

const EditableCell = ({
  editing,
  dataIndex,
  children,
  ...restProps
}) => {
  return (
    <td {...restProps}>
      {editing ? (
        <Form.Item
          name={dataIndex}
          style={{
            margin: 0,
          }}
          rules={[
            {
              required: true,
              message: `请输入提示学习模板!`,
            },
          ]}
        >
          <TextArea placeholder='请输入提示学习模板' allowClear />
        </Form.Item>
      ) : (
        <span style={{ width:540, wordWrap: 'break-word', wordBreak: 'break-word' }}>{children}</span>
      )}
    </td>
  );
};

export const PromptLearnTemplate = React.forwardRef(({ projectId,...props },ref)=>{
  const [form] = Form.useForm();
  const [sourceData, setSourceData] = useState([]);
  const [count, setCount] = useState(0);
  const [editingKey, setEditingKey] = useState('');
  const [dlgVisible, setDlgVisible] = useState(false);
  const [loading,setLoading] = useState(true);
  const api = useAPI();

  const isEditing = (record) => record.key === editingKey || record.isNew;

  const showDlg = () => {
    setDlgVisible(true);
    mlPromptTemplateQuery();
  };

  useImperativeHandle(ref, () => ({
    show:showDlg,
  }));

  const mlPromptTemplateQuery = useCallback(async () => {
    const tmps = await api.callApi('mlPromptTemplateQuery', {
      params: { project_id: projectId },
    });

    setLoading(false);
    return tmps;
  }, [projectId]);

  const mlPromptPredict = useCallback(async () => {
    return await api.callApi('mlPromptPredict', {
      params: {
        project: projectId,
      },
    });
  }, [projectId]);

  const mlPromptTemplateCreate = async (project,template) => {
    return await api.callApi('mlPromptTemplateCreate', {
      body: {
        project,
        template,
        taskId:1,
      },
    });
  };

  const execPredict = async () => {
    try {
      await form.validateFields();
      mlPromptPredict();
      setDlgVisible(false);
    }catch(e){console.log(e);}
  };

  const edit = (record) => {
    form.setFieldsValue({
      template: '',
      isNew:false,
      ...record,
    });
    setEditingKey(record.key);
  };

  const cancel = (record) => {
    form.setFieldsValue({
      template:'',
    });
    if (record.isNew) {
      handleDelete(record.key);
    } else {
      setEditingKey('');
    }
  };

  const handleDelete = (key) => {
    const newData = sourceData.filter((item) => item.key !== key);

    setSourceData(newData);
  };

  const handleAdd = () => {
    const newData = {
      key: count,
      template: '',
      isNew:true,
    };

    setSourceData([newData,...sourceData]);
    setCount(count + 1);
  };

  const save = async (key) => {
    try {
      const row = await form.validateFields();

      row.isNew=false;
      const newData = [...sourceData];
      const index = newData.findIndex((item) => key === item.key);

      if (index > -1) {
        const item = newData[index];

        newData.splice(index, 1, { ...item, ...row });
        setSourceData(newData);
        setEditingKey('');
      } else {
        setSourceData([...newData,row]);
        setEditingKey('');
      }

      form.setFieldsValue({
        template:'',
      });
      mlPromptTemplateCreate(projectId,row.template);
    } catch (errInfo) {
      console.log('Validate Failed:', errInfo);
    }
  };

  const strTip = `[dlg]代表整个对话，[dlg1]代表对话第一行，[dlg2]代表对话第二行，[dlgx]代表对话第x行，[mask]代表被遮罩的内容。`;

  const columns = [
    {
      title: () => {
        return (
          <>
            提示学习模板
            <Tooltip title={strTip} overlayInnerStyle={{ borderRadius: 5 }} >
              <Icon icon={FaQuestionCircle} style={{ opacity: 0.5,marginTop:3 }} />
            </Tooltip>
          </>
        );
      },
      dataIndex: 'template',
      width: 540,
      editable: true,
    },
    {
      title: '操作',
      dataIndex: 'operation',
      render: (_, record) => {
        console.log(_);
        const editable = isEditing(record);

        return editable ? (
          <span>
            <Typography.Link
              onClick={() => save(record.key)}
              style={{
                marginRight: 8,
              }}
            >
            保存
            </Typography.Link>
            <Popconfirm title="确定取消吗?" okText="是" cancelText="否" onConfirm={() => { cancel(record);}}>
              <a>取消</a>
            </Popconfirm>
          </span>
        ) : (
          <span>
            <Space size="middle">
              <a onClick={() => edit(record)}>修改</a>
              <Popconfirm title="确定删除吗?" okText="是" cancelText="否" onConfirm={() => handleDelete(record.key)}>
                <a>删除</a>
              </Popconfirm>
            </Space>
          </span>
        );
      },
    },
  ];

  const mergedColumns = columns.map((col) => {
    if (!col.editable) {
      return col;
    }

    return {
      ...col,
      onCell: (record) => ({
        record,
        dataIndex: col.dataIndex,
        editing: isEditing(record),
      }),
    };
  });

  return (
    dlgVisible && (
      <Modal style={{ width:800 }} visible bare closeOnClickOutside={false}>
        <div className={'dlg-root'}>
          <Modal.Header>
            <span style={{ fontSize: 16,fontWeight:700 }}>预标注(提示学习)</span>
          </Modal.Header>
          <div className={'dlg-content'}>
            <Form form={form} component={false}>
              <Button
                onClick={handleAdd}
                disabled={loading}
                type="primary"
                size={'small'}
                style={{
                  marginBottom: 5,
                  float:'right',
                }}
                icon={<PlusOutlined />}
              >
                新增
              </Button>
              <Table
                loading={loading}
                components={{
                  body: {
                    cell: EditableCell,
                  },
                }}
                dataSource={sourceData}
                columns={mergedColumns}
                rowClassName="editable-row"
                pagination={{
                  onChange: cancel,
                  position: ['bottomLeft'],
                  pageSize: 5,
                  size:'small',
                  showTotal:(total, range) => `${range[0]}-${range[1]} 共 ${total}`,
                }}
              />
            </Form>
          </div>
          <Modal.Footer>
            <div style={{ marginRight:20 }}>
              <Space align="end">
                <Button
                  onClick={() => {
                    setDlgVisible(false);
                    setSourceData([]);
                  }}
                  size="compact"
                  autoFocus
                >
                取消
                </Button>
                <Button
                  disabled={loading || sourceData.length===0}
                  onClick={execPredict}
                  size="compact"
                  type="primary"
                >
                立即运行
                </Button>
              </Space>
            </div>
          </Modal.Footer>
        </div>
      </Modal>
    )
  );
});
