import { forwardRef, useCallback, useEffect, useImperativeHandle, useMemo, useRef } from "react";
import { Button, Col, Row, Select, Space } from 'antd';
import { ProTable } from "@ant-design/pro-components";
import { Modal } from "@/components/Modal/Modal";
import "./index.less";

const formItemLayout = {
  labelCol: { span: 4 },
  wrapperCol: { span: 20 },
};

export default forwardRef(({ project }, ref) => {
  const modalRef = useRef();

  useImperativeHandle(ref, () => ({
    show: () => {
      modalRef.current?.show();
    },
  }));

  const onCancel = useCallback(() => {
    modalRef.current?.hide();
  }, [modalRef]);

  const request = useCallback(() => {
    return {
      data: [{
        id: 1,
        prev_model: '移动模型3.0',
        project: '6月涨薪',
        label_count: '300',
        task_count: '300',
        is_train: true,
        prev_precision_rate: '90%',
        next_precision_rate: '88%',
        next_model: '移动模型3.1',
        next_train_task: '500',
        next_evaluate_task: '400',
        train_rate: '77%',
        project_collection: '移动模型',
        time: '2022-03-04 11:11:11',
        operator: '西征',
      }],
      success: true,
      totla: 1,
    };
  }, []);

  // TEMP
  // useEffect(() => {
  //   modalRef.current?.show();
  // }, []);

  return (
    <Modal
      bare
      ref={modalRef}
      className="human-zone"
      style={{
        width: "calc(100vw - 96px)",
        minWidth: 1000,
        minHeight: 500,
      }}
    >
      <Modal.Header>人在环路</Modal.Header>
      <ProTable
        options={false}
        search={false}
        request={request}
        rowKey='id'
        headerTitle={(
          <Space>
            <Select placeholder="训练前模型" />
            <Select placeholder="操作人" />
            <Select placeholder="是否训练" />
            <Select placeholder="项目集合" />
          </Space>
        )}
        toolBarRender={() => [
          <Button key="cancel" onClick={onCancel}>取消</Button>,
          <Button type="primary" key="add_evaluate">新增评估</Button>,
          <Button type="primary" key="add_train">新增训练</Button>,
        ]}
        columns={[
          {
            title: '训练前模型',
            dataIndex: 'prev_model',
            render: v => {
              return <Button type="link">{v}</Button>;
            },
          },
          {
            title: '项目',
            dataIndex: 'project',
          },
          {
            title: '正确标注数',
            dataIndex: 'label_count',
          },
          {
            title: '总任务数',
            dataIndex: 'task_count',
          },
          {
            title: '是否训练',
            dataIndex: 'is_train',
          },
          {
            title: '当前准确率',
            dataIndex: 'prev_precision_rate',
          },
          {
            title: '新模型准确率',
            dataIndex: 'next_precision_rate',
          },
          {
            title: '新模型',
            dataIndex: 'next_model',
            render: v => {
              return <Button type="link">{v}</Button>;
            },
          },
          {
            title: '新模型训练任务数',
            dataIndex: 'next_train_task',
          },
          {
            title: '新模型评估任务数',
            dataIndex: 'next_evaluate_task',
          },
          {
            title: '训练进度',
            dataIndex: 'train_rate',
          },
          {
            title: '项目集合',
            dataIndex: 'project_collection',
          },
          {
            title: '时间',
            dataIndex: 'time',
          },
          {
            title: '操作人',
            dataIndex: 'operator',
          },
          {
            title: '操作',
            render: () => {
              return <Button type="link">删除</Button>;
            },
          },
        ]}
      />
    </Modal>
  );
});
