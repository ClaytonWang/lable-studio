import React, { useState } from 'react';
import { Select } from '../../../components/Form/Elements';
import { Col, Form, Row } from 'antd';
import { Button } from '../../../components';
import "./SearchBar.less";

export const SearchBar = (props) => {
  const [form] = Form.useForm();

  const columns = [
    {
      key: "type",
      label: "模型类型",
      value:'',
      data: [
        '',
        'intention',
        'clean',
      ],
      render: (col) => {
        return (
          <Select
            value={col.value}
            options={col.data.map(v => ({ label: `${v}`, value: v }))}
            onChange={(e) => {
              col.value = e.target.value;
            }}
          />
        );
      },
    },
    {
      key: "version",
      label: "版本号",
      value:'',
      data: [
        'intention',
        'clean',
      ],
      render: (col) => {
        return (
          <Select
            value={col.value}
            options={col.data.map(v => ({ label: `${v}`, value: v }))}
            onChange={(e) => {
              col.value = e.target.value;
            }}
          />
        );
      },
    },
    {
      key: "model_set",
      label: "模型集",
      value:'',
      data: [
        'intention',
        'clean',
      ],
      render: (col) => {
        return (
          <Select
            value={col.value}
            options={col.data.map(v => ({ label: `${v}`, value: v }))}
            onChange={(e) => {
              col.value = e.target.value;
            }}
          />
        );
      },
    },
    {
      key: "project_set",
      label: "项目集",
      value:'',
      data: [
        'intention',
        'clean',
      ],
      render: (col) => {
        return (
          <Select
            value={col.value}
            options={col.data.map(v => ({ label: `${v}`, value: v }))}
            onChange={(e) => {
              col.value = e.target.value;
            }}
          />
        );
      },
    },
  ];

  const getFields = () => {
    const children = columns.map((col) => {
      const { key, label, render } = col;

      return (
        <Col span={5} key={key}>
          <Form.Item name={`field-${key}`} label={label}>
            {render?.(col)}
          </Form.Item>
        </Col>
      );
    });

    children.push(
      <Col
        key={ 'action'}
        span={4}
        style={{
          textAlign: 'right',
        }}
      >
        <Button look="primary" size="compact">搜索</Button>
        <Button
          size="compact"
          style={{
            margin: '0 8px',
          }}
          onClick={() => {
            form.resetFields();
          }}
        >
          清除
        </Button>
      </Col>,
    );
    return children;
  };

  const onFinish = (values) => {
    console.log('Received values of form: ', values);
  };

  return (
    <Form
      form={form}
      name="advanced_search"
      className="ant-advanced-search-form"
      onFinish={onFinish}
    >
      <Row gutter={20}>{getFields()}</Row>
    </Form>
  );
};
