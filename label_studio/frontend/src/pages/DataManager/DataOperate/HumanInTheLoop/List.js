import { useCallback } from "react";
import { Button, Select, Space, Tooltip } from "antd";
import { QuestionCircleOutlined } from "@ant-design/icons";
import { ProTable } from "@ant-design/pro-components";
import { PlusOutlined } from "@ant-design/icons";
import { Modal } from "@/components/Modal/Modal";

export default ({ onCancel, onEvaluate, onTrain }) => {
  const request = useCallback(() => {
    return {
      data: [
        {
          id: 1,
          prev_model: "移动模型3.0",
          project: "6月涨薪",
          label_count: "300",
          task_count: "300",
          is_train: true,
          prev_precision_rate: "90%",
          next_precision_rate: "88%",
          next_model: "移动模型3.1",
          next_train_task: "500",
          next_evaluate_task: "400",
          train_rate: "77%",
          project_collection: "移动模型",
          time: "2022-03-04 11:11:11",
          operator: "西征",
        },
      ],
      success: true,
      totla: 1,
    };
  }, []);

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
        request={request}
        rowKey="id"
        headerTitle={(
          <Space>
            <Select key="0" placeholder="训练前模型" />
            <Select key="1"  placeholder="操作人" />
            <Select key="2"  placeholder="是否训练" />
            <Select key="3"  placeholder="项目集合" />
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
              return <Button type="link">删除</Button>;
            },
          },
        ]}
      />
    </>
  );
};
