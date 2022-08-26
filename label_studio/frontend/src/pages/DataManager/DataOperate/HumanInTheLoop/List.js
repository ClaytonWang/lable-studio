import { useCallback ,useContext, useEffect,useState } from "react";
import { Button, Popconfirm, Select, Space,Tooltip } from "antd";
import { ExclamationCircleOutlined,QuestionCircleOutlined } from "@ant-design/icons";
import { ProTable } from "@ant-design/pro-components";
import { PlusOutlined } from "@ant-design/icons";
import { Modal } from "@/components/Modal/Modal";
import { ApiContext } from '@/providers/ApiProvider';
import { useProject } from "@/providers/ProjectProvider";
const { Option } = Select;

export default ({ onCancel, onEvaluate, onTrain }) => {
  const api = useContext(ApiContext);
  const { project } = useProject();
  const [prevModels, setPrevModels] = useState([]);
  const [operators, setOperators] = useState([]);
  const [projectSets, setProjectSets] = useState([]);

  const getListData = useCallback(async () => {
    if (!project.id) {
      return {};
    }
    const result = await api.callApi("listTrain", {
      params: {
        project_id:project.id,
      },
    });

    return {
      data: result.results,
      success: true,
      total: result.count,
    };

  }, [project]);

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
    },[project]);

  useEffect(async () => {
    selectOfTrain().then((data) => {
      setPrevModels(data?.models);
      setOperators(data?.users);
      setProjectSets(data?.project_sets);
    });

  },[]);

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
        options={false}
        search={false}
        request={getListData}
        rowKey="id"
        headerTitle={(
          <Space>
            <Select key="0" placeholder="训练前模型" >
              {prevModels.map((model) => (
                <Option key={model.id}>{model.title}</Option>
              ))}
            </Select>
            <Select key="1" placeholder="操作人" >
              {operators.map((user) => (
                <Option key={user}>{user}</Option>
              ))}
            </Select>
            <Select key="2" placeholder="是否训练">
              <Option key="true">是</Option>
              <Option key="false">否</Option>
            </Select>
            <Select key="3" placeholder="项目集合" >
              {projectSets.map((proj) => (
                <Option key={proj.id}>{proj.title}</Option>
              ))}
            </Select>
          </Space>
        )}
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
            dataIndex: "prev_model",
            render: (v) => {
              return <Button type="link">{v}</Button>;
            },
          },
          {
            title: "项目",
            dataIndex: "project",
          },
          {
            title: "正确标注数",
            dataIndex: "label_count",
          },
          {
            title: "总任务数",
            dataIndex: "task_count",
          },
          {
            title: "是否训练",
            dataIndex: "is_train",
          },
          {
            title: "当前准确率",
            dataIndex: "prev_precision_rate",
          },
          {
            title: "新模型准确率",
            dataIndex: "next_precision_rate",
          },
          {
            title: "新模型",
            dataIndex: "next_model",
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
            dataIndex: "next_train_task",
          },
          {
            title: (
              <Tooltip title={t("next_evaluate_task_count")}>
                新模型评估任务数
              </Tooltip>
            ),
            dataIndex: "next_evaluate_task",
          },
          {
            title: "训练进度",
            dataIndex: "train_rate",
          },
          {
            title: "项目集合",
            dataIndex: "project_collection",
          },
          {
            title: "时间",
            dataIndex: "time",
          },
          {
            title: "操作人",
            dataIndex: "operator",
          },
          {
            title: "操作",
            render: () => {
              return (
                <Popconfirm
                  title="确定要删除当前记录吗?"
                  onConfirm={() => { }}
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
