import React from "react";
import { Col, Form, Row } from "antd";
import { SearchOutlined } from "@ant-design/icons";
import { Button } from "../../../components";
import { Select } from "../../../components/Form/Elements";
import "./SearchBar.less";
import { useFilter } from "./useFilter";

const getFilters = (filters) => {
  const model_types = ["none"].concat(Object.keys(filters?.type ?? []).sort());
  const model_versions = ["none"].concat((filters.version ?? []).sort());

  return [
    {
      key: "type",
      label: "模型类型",
      value: "none",
      data: model_types,
      render: (col) => {
        return (
          <Select
            value={col.value}
            options={col.data.map((v) => {
              if (v === "none") {
                return { label: "不限", value: v };
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
      value: "none",
      data: model_versions,
      render: (col) => {
        return (
          <Select
            value={col.value}
            options={col.data.map((v) => {
              if (v === "none") {
                return { label: "不限", value: v };
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
};

export const SearchBar = React.memo((props) => {
  const [form] = Form.useForm();
  const filters = useFilter();
  const fields = getFilters(filters);

  const handleSearch = async () => {
    if (props.onSearch) {
      const obj = {};

      fields.map((v) => {
        obj[v.key] = v.value === "none" ? "" : v.value;
      });
      await props.onSearch(props.pageSize, {
        type: obj["type"],
        version: obj["version"],
        mdoel_set: obj["model_set"],
      });
    }
  };

  const getFields = () => {
    const children = fields.map?.((col) => {
      const { key, label, render } = col;

      return (
        <Col span={5} key={key}>
          <Form.Item name={`${key}`} label={label}>
            {render?.(col)}
          </Form.Item>
        </Col>
      );
    });

    children?.push(
      <Col
        key={"action"}
        span={4}
        style={{
          textAlign: "left",
        }}
      >
        <Button
          look="primary"
          size="compact"
          onClick={handleSearch}
          icon={<SearchOutlined style={{ width: 20, height: 20 }} />}
        >
          搜索
        </Button>
      </Col>,
    );
    return children;
  };

  return (
    <Form
      fields={fields}
      form={form}
      className="ant-advanced-search-form"
      colon={false}
    >
      <Row gutter={20}>{getFields()}</Row>
    </Form>
  );
});
