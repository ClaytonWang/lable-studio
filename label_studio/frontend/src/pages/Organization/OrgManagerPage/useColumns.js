import { Space } from '@/components/Space/Space';
import { Elem } from '@/utils/bem';
import { Userpic } from '@/components';
import { format } from 'date-fns';
import React, { useCallback, useContext, useMemo, useState } from 'react';
import { Popconfirm } from 'antd';
import { ExclamationCircleOutlined, InfoCircleOutlined } from "@ant-design/icons";
import { ApiContext } from '../../../providers/ApiProvider';
import { useHistory } from "react-router";


export const useColumns = (reload) => {
  const api = useContext(ApiContext);
  const history = useHistory();
  const [modalAddEdit, setModalAddEdit] = useState(null);
  const [modalEdt, setModaEdt] = useState(null);

  const changeOrg = useCallback(
    async (record) => {
      await api.callApi("changeOrg", {
        body: { organization_id: record.id },
      });
      history.replace("/organization");
    },[]);

  const deleteOrg = useCallback(
    async (record) => {
      await api.callApi("deleteOrg", {
        body: { organization_id: record.id },
      });
      reload();
    },[]);

  const columns = useMemo(() => {
    return [
      {
        title: '组织名称',
        dataIndex: 'title',
        key: 'title',
        render: (_, record) => {
          return record.title;
        },
      },
      {
        title: '创建时间',
        dataIndex: 'created_at',
        key: 'created_at',
        render: (_, record) => {
          return (
            <Elem name="created-date">
              {format(new Date(record.created_at), "yyyy-MM-dd HH:mm")}
            </Elem>
          );
        },
      },
      {
        title: '创建人',
        dataIndex: 'created_by',
        key: 'created_by',
        render: (_, record) => {
          return (
            <Elem name="created-by">
              <Userpic src="#" user={record.created_by} showUsername />
            </Elem>
          );
        },
      },
      {
        title: '操作',
        dataIndex: 'action',
        key: 'action',
        render: (_, record) => (
          <Space size="middle">
            <Popconfirm
              title={(record.project_count || record.user_count) ? "是否确定删除该组织?" : "该组织包含有效用户或项目,无法删除."}
              onConfirm={() => { deleteOrg(record); }}
              icon={(record.project_count || record.user_count) ? <InfoCircleOutlined /> : <ExclamationCircleOutlined style={{ color: 'red' }} />}
              okText="确定"
              cancelText="取消"
              showCancel={!!(record.project_count || record.user_count)}
            >
              <a onClick={() => { setModaEdt(record); }}>删除</a>
            </Popconfirm>

            <a onClick={() => { setModalAddEdit(record); }}>编辑</a>

            <Popconfirm
              title="确定要切换当前组织吗?"
              onConfirm={() => { changeOrg(record); }}
              icon={<InfoCircleOutlined />}
              okText="确定"
              cancelText="取消">
              <a>切换</a>
            </Popconfirm>
          </Space>
        ),
      },
    ];
  }, []);

  return {
    columns,
    modalAddEdit,
    setModalAddEdit,
    modalEdt,
    setModaEdt,
  };
};
