import React, { useCallback, useState } from 'react';
import { useHistory } from "react-router";
import { Modal } from '../../../components/Modal/Modal';
import { cn } from '../../../utils/bem';
import { Form } from 'antd';
import { Button } from '../../../components';
import { Input,Select } from '../../../components/Form';

export const ModelImport = ({ onClose }) => {
  const rootClass = cn("create-project");
  const [form] = Form.useForm();
  const history = useHistory();

  const onHide = useCallback(async () => {
    history.replace("/model-configer");
    onClose?.();
  }, []);

  const layout = {
    labelCol: {
      span: 6,
    },
    wrapperCol: {
      span: 18,
    },
  };
  const tailLayout = {
    wrapperCol: {
      offset: 8,
      span: 16,
    },
  };

  return (
    <Modal style={{ width: 500 }}
      onHide={onHide}
      visible
      closeOnClickOutside={false}
      allowClose={true}
      title={t("Import Model")}
    >
      <Form
        className={rootClass}
        {...layout}
        form={form}
        layout="horizontal"
        name="form_in_modal"
      >
        <Form.Item
          name="title"
          label="模型名称"
          rules={[
            {
              required: true,
              message: '请输入模型名称,且不能超过20个字符。',
            },
          ]}
        >
          <Input placeholder="模型名称"/>
        </Form.Item>
        <Form.Item
          name="model_type"
          label="类型"
          rules={[{
            required: true,
            message: '请选择模型类型。',
          }]}>
          <Select
            defaultValue={null}
            options={[
              { label: '对话意图分类', value: 'intention' },
              { label: '对话生成', value: 'generation' },
              { label: '清洗模型', value: 'clean' },
              { label: '其他', value: 'other' },
            ]}
            placeholder={t("Please select Model type")}
          />
        </Form.Item>
        <Form.Item
          name="title"
          label="URL"
          rules={[
            {
              required: true,
              message: '请输入模型对应的URL。',
            },
          ]}
        >
          <Input placeholder="模型URL"/>
        </Form.Item>
        <Form.Item {...tailLayout}>
          <Button type="primary" >
              取消
          </Button>
          <Button htmlType="button">
              立即导入
          </Button>
        </Form.Item>
      </Form>
    </Modal>
  );
};
