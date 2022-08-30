import { useCallback ,useContext, useEffect,useRef,useState } from "react";
import { Button, Popconfirm, Select, Space,Tooltip } from "antd";
import { ExclamationCircleOutlined,QuestionCircleOutlined } from "@ant-design/icons";
import { ProTable } from "@ant-design/pro-components";
import { PlusOutlined } from "@ant-design/icons";
import { Modal } from "@/components/Modal/Modal";
import { ApiContext } from '@/providers/ApiProvider';
import { useProject } from "@/providers/ProjectProvider";
import { Userpic } from '@/components';
import { format } from 'date-fns';
const { Option } = Select;

export default ({ onCancel, onEvaluate, onTrain }) => {
  const api = useContext(ApiContext);
  const { project } = useProject();
  const [prevModels, setPrevModels] = useState([]);
  const [prevModelId, setPrevModelId] = useState('');
  const [operators, setOperators] = useState([]);
  const [operatorId, setOperatorId] = useState('');
  const [isTrain, setIsTrain] = useState('');
  const [projectSetId, setProjectSetId] = useState('');
  const [projectSets, setProjectSets] = useState([]);
  const ref = useRef();

  const getListData = async (params = {}) => {
    if (!project.id) {
      return {};
    }
    const result = await api.callApi("listTrain", {
      params: {
        project_id: project.id,
        page: params.current,
        page_size: params.pageSize,
        model_id:prevModelId,
        user_id: operatorId,
        is_train: isTrain,
        project_set_id:projectSetId,
      },
    });

    return {
      data: result.results,
      success: true,
      total: result.count,
    };

  };

  const selectOfTrain = useCallback(
    async () => {
      if (!project.id) {
        return {};
      }
      return await api.callApi("selectOfTrain", {
        params: {
          project_id:project.id,
        },
      });
    }, [project]);

  const deleteData = useCallback(
    async (id) => {
      await api.callApi("delTrain", {
        params: {
          pk:id,
        },
      }).then(() => {
        ref.current.reload();
      });
    }, []);

  useEffect(async () => {
    selectOfTrain().then((data) => {
      setPrevModels(data?.models);
      setOperators(data?.users);
      setProjectSets(data?.project_sets);
    });

  },[]);

  const formatNumber = (value) => {
    if (!value)
      value = 0;
    try {
      value = parseFloat(value) * 100;
    } catch (e) {
      value = 0;
    }
    return new Intl.NumberFormat('en', {
      style: 'unit',
      unit: 'percent',
    }).format(value);
  };

  const modelChange = (e) => {
    setPrevModelId(e);
    ref.current.reload();
  };

  const operatorChange = (e) => {
    setOperatorId(e);
    ref.current.reload();
  };

  const isTrainChange = (e) => {
    setIsTrain(e);
    ref.current.reload();
  };

  const projectChange = (e) => {
    setProjectSetId(e);
    ref.current.reload();
  };

  return (
    <>
      <Modal.Header>
        <Space>
          <span>人在环路</span>
          <Tooltip title={t("tip_human_loop", "用户审核修改自动标注结果后，可通过【+新增评估】功能记录当前准确率。或通过【+新增训练】功能训练更精准的新模型。")}>
            <QuestionCircleOutlined />
          </Tooltip>
        </Space>
      </Modal.Header>
      <ProTable
        actionRef={ref}
        search={false}
        request={getListData}
        rowKey="id"
        options={false}
        headerTitle={(
          <Space>
            <Select key="0" placeholder="训练前模型" onChange={modelChange} >
              <Option key="">不限</Option>
              {prevModels.map((model) => (
                <Option key={model.id}>{model.title} { model.version}</Option>
              ))}
            </Select>
            <Select key="1" placeholder="操作人" onChange={operatorChange} >
              <Option key="">不限</Option>
              {operators.map((user) => (
                <Option key={user.user_id}>{user.username}</Option>
              ))}
            </Select>
            <Select key="2" placeholder="是否训练" onChange={isTrainChange} >
              <Option key="">不限</Option>
              <Option key="true">是</Option>
              <Option key="false">否</Option>
            </Select>
            <Select key="3" placeholder="项目集合" onChange={projectChange} >
              <Option key="">不限</Option>
              {projectSets.map((proj) => (
                <Option key={proj.id}>{proj.title}</Option>
              ))}
            </Select>
          </Space>
        )}
        pagination={{
          pageSize: 5,
          showSizeChanger: true,
        }}
        toolBarRender={() => [
          <Button key="cancel" onClick={onCancel}>
            取消
          </Button>,
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={onEvaluate}
            key="add_evaluate"
          >
            新增评估
          </Button>,
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={onTrain}
            key="add_train"
          >
            新增训练
          </Button>,
        ]}
        columns={[
          {
            title: "训练前模型",
            dataIndex: "model_title_version",
            render: (v,record) => {
              return (record.category === "train" ? <Button type="link">{v}</Button> : { v });
            },
          },
          {
            title: "项目",
            dataIndex: "project_title",
          },
          {
            title: "正确标注数",
            dataIndex: "exactness_count",
          },
          {
            title: "总任务数",
            dataIndex: "total_count",
          },
          {
            title: "是否训练",
            dataIndex: "is_train",
            render: (_,record) => {
              return (
                <div>
                  {record.is_train?'是':'否'}
                </div>
              );
            },
          },
          {
            title: "当前准确率",
            dataIndex: "accuracy_rate",
            render: (_,record) => {
              return (
                <div>
                  {formatNumber(record.accuracy_rate)}
                </div>
              );
            },
          },
          {
            title: "新模型准确率",
            dataIndex: "new_accuracy_rate",
            render: (_,record) => {
              return (
                <div>
                  {formatNumber(record.new_accuracy_rate)}
                </div>
              );
            },
          },
          {
            title: "新模型",
            dataIndex: "new_model_title_version",
            render: (v) => {
              return <Button type="link">{v}</Button>;
            },
          },
          {
            title: (
              <Tooltip title={t("next_train_task_count")}>
                新模型训练任务数
              </Tooltip>
            ),
            dataIndex: "new_model_train_task",
          },
          {
            title: (
              <Tooltip title={t("next_evaluate_task_count")}>
                新模型评估任务数
              </Tooltip>
            ),
            dataIndex: "new_model_assessment_task",
          },
          {
            title: "训练进度",
            dataIndex: "training_progress",
            render: (_,record) => {
              return (
                <div >
                  {formatNumber(record.training_progress)}
                </div>
              );
            },
          },
          {
            title: "项目集合",
            dataIndex: "project_set",
          },
          {
            title: "时间",
            dataIndex: "updated_at",
            render: (_, record) => {
              return (
                <div name="created-date">
                  {format(new Date(record.created_at), "yyyy-MM-dd HH:mm")}
                </div>
              );
            },
          },
          {
            title: "操作人",
            dataIndex: 'created_by',
            render: (_, record) => {
              return (
                <div name="created-by">
                  <Userpic src="#" user={record.created_by} showUsername />
                </div>
              );
            },
          },
          {
            title: "操作",
            render: (_,record) => {
              return (
                <Popconfirm
                  title="确定要删除当前记录吗?"
                  onConfirm={() => { deleteData(record.id);}}
                  icon={<ExclamationCircleOutlined style={{ color: 'red' }}  />}
                  okText="确定"
                  cancelText="取消">
                  <Button type="link">删除</Button>
                </Popconfirm>
              );

            },
          },
        ]}
      />
    </>
  );
};
