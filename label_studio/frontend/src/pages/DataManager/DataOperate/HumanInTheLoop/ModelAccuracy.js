import React, { useContext, useEffect, useState } from 'react';
import { Table } from "antd";
import { Modal } from "@/components/Modal/Modal";
import { Space } from "@/components/Space/Space";
import { Button } from "@/components/Button/Button";
import { ApiContext } from '@/providers/ApiProvider';
import { format } from 'date-fns';
import { Userpic } from '@/components';

export default ({ onCancel ,evalId,modelId }) => {
  const api = useContext(ApiContext);
  const [dataSource, setDataSource] = useState([]);
  const [loading, setLoading] = useState(false);

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

  const getListData = async (pk,model_id) => {
    if (!pk) {
      return [];
    }
    return await api.callApi("accuracy", {
      params: {
        pk,
        model_id,
      },
    });
  };

  const columns = [
    {
      title: '模型',
      dataIndex: 'model__title',
      key: 'model__title',
      render: (_, record) => {
        return record.model__title+record.model__version;
      },
    },
    {
      title: '项目',
      dataIndex: 'project__title',
      key: 'project__title',
    },
    {
      title: "准确率",
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
  ];

  useEffect(() => {
    setLoading(true);
    getListData(evalId,modelId).then(data => {
      setLoading(false);
      setDataSource(data);
    });
  }, [modelId]);


  return (
    <div className="evaluate">
      <Modal.Header>
        <span>
          模型准确率
        </span>
      </Modal.Header>
      <Table
        style={{ paddingLeft:24,paddingRight:24,marginBottom:-1 }}
        rowKey="id"
        columns={columns}
        dataSource={dataSource}
        pagination={{
          pageSize: 5,
          showSizeChanger: true,
          pageSizeOptions:[5,10,20],
        }}
        loading={loading} />
      <Modal.Footer>
        <Space align="end">
          <Button size="compact" onClick={onCancel}>返回</Button>
        </Space>
      </Modal.Footer>
    </div>
  );
};
