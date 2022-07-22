import React, { useCallback ,useState } from 'react';
import { Select } from '../../../components/Form/Elements';
import { Col, Form, Row } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import { Button } from '../../../components';
import "./SearchBar.less";

const columns = [
  {
    key: "type",
    label: "模型类型",
    value:'none',
    data: [
      'none',
      'intention',
      'clean',
      'generation',
      'other',
    ],
    render: (col) => {
      return (
        <Select
          value={col.value}
          options={col.data.map(v => {
            if (v === 'none') {
              return { label: '不限', value: v };
            } else {
              return { label: t(v), value: v };
            }
          })}
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
    value:'none',
    data: [
      'none',
      'v1',
      'v2',
    ],
    render: (col) => {
      return (
        <Select
          value={col.value}
          options={col.data.map(v => {
            if (v === 'none') {
              return { label: '不限', value: v };
            } else {
              return { label: t(v), value: v };
            }
          })}
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
    value:'none',
    data: [
      'none',
    ],
    render: (col) => {
      return (
        <Select
          value={col.value}
          options={col.data.map(v => {
            if (v === 'none') {
              return { label: '不限', value: v };
            } else {
              return { label: t(v), value: v };
            }
          })}
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
    value:'none',
    data: [
      'none',
    ],
    render: (col) => {
      return (
        <Select
          value={col.value}
          options={col.data.map(v => {
            if (v === 'none') {
              return { label: '不限', value: v };
            } else {
              return { label: t(v), value: v };
            }
          })}
          onChange={(e) => {
            col.value = e.target.value;
          }}
        />
      );
    },
  },
];

export const SearchBar = (props) => {
  const [form] = Form.useForm();
  const [fields, setFields] = useState(columns);

  const handleSearch = useCallback(async () => {
    if (props.onSearch) {
      const obj = {};

      fields.map((v) => {
        obj[v.key]=v.value==='none'?'':v.value;
      });
      await props.onSearch(props.pageSize, { type:obj['type'], version:obj['version'], mdoel_group:obj['model_set'], project_group:obj['project_set'] });
    }
  }, [props.onSearch]);

  const getFields = () => {
    const children = columns.map((col) => {
      const { key, label, render } = col;

      return (
        <Col span={5} key={key}>
          <Form.Item name={`${key}`} label={label}>
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
          textAlign: 'left',
        }}
      >
        <Button look="primary" size="compact" onClick={handleSearch} icon={<SearchOutlined style={{ width:20,height:20 }}/>}>搜索</Button>
        {/* <Button
          size="compact"
          style={{
            margin: '0 8px',
          }}
          onClick={() => {
            form.resetFields();
          }}
        >
          清除
        </Button> */}
      </Col>,
    );
    return children;
  };

  return (
    <Form
      fields={fields}
      form={form}
      className="ant-advanced-search-form"
    >
      <Row gutter={20}>{getFields()}</Row>
    </Form>
  );
};
