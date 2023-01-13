import { Elem } from '../../../utils/bem';
import { Userpic } from '../../../components';
import { format } from 'date-fns';
import { useMemo, useState } from 'react';
import { LoadingOutlined } from '@ant-design/icons';
import { Button,Space,Spin } from 'antd';
import { confirm } from "@/components/Modal/Modal";
import { useAPI } from "@/providers/ApiProvider";
import { useConfig } from "@/providers/ConfigProvider";

const ModelState = {
  1: "初始",
  2: "评估",
  3: "训练中...",
  4: "已完成",
  5: "失败",
  6: "运行中",
};

const loadingIcon = (
  <LoadingOutlined
    style={{
      fontSize: 24,
    }}
    spin
  />
);

export const useColumns = () => {
  const [modalExp, setModalExp] = useState(null);
  const [modalEdt, setModaEdt] = useState(null);
  const api = useAPI();
  const config = useConfig();

  const handlDel = (model) => {
    confirm({
      title: "删除模型",
      body: "是否要删除模型？",
      buttonLook: "destructive",
      onOk: () => delModel(model),
      okText: "删除",
      cancelText: t("Cancel"),
    });
  };

  const delModel = (model) => {
    api.callApi("deleteModel", {
      params: {
        pk: model.id,
      },
    })
      .then((res) => {
        location.reload();
      });
  };

  const columns = useMemo(() => {
    return [
      {
        title: '模型名称',
        dataIndex: 'title_version',
        key: 'title_version',
        render: (_, record) => {
          if (record.type === 'clean')
            return (
              <Elem name="title_version">
                {_}
              </Elem>
            );
          else
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
        title: '版本号',
        dataIndex: 'version',
        key: 'version',
        render: (_, record) => {
          return (
            <Elem name="version">
              {record.version}
            </Elem>
          );
        },
      },
      {
        title: '模型类型',
        dataIndex: 'type',
        key: 'type',
        render: (_, record) => {
          return (
            <Elem name="type">
              {record.model_type}
            </Elem>
          );
        },
      },
      {
        title: '项目',
        dataIndex: 'project',
        key: 'project',
        render: (_, record) => {
          if (!record.project) return '';
          return record.project;
        },
      },
      {
        title: '状态',
        dataIndex: 'state',
        key: 'state',
        render: (_, record) => {
          if (!record.state) return '/';
          return ModelState[record.state];
        },
      },
      {
        title: '操作',
        dataIndex: 'action',
        key: 'action',
        render: (_, record) => (
          <>
            {
              (() => {
                return [
                  record.state === 3 ? <Spin indicator={loadingIcon} /> : <Button type="link" key="export" size="small" disabled={ record.state === 5} onClick={() => { setModalExp(record); }}>导出</Button>,
                  (record.version === "1.0" && record.state === 4) || record.state === 3 || config.user?.group === "user" ? null : (<Button type="link" key="del" size="small" style={{ color: 'red' }} onClick={() => { handlDel(record); }}>删除</Button>),
                  record.type === "rule" && record.state === 4 ? (<Button type="link" key="edit" size="small" onClick={() => { setModaEdt(record); }}>编辑参数</Button>) : null,
                ];
              })()
            }
          </>
        ),
      },
    ];
  }, []);

  return {
    columns,
    modalExp,
    setModalExp,
    modalEdt,
    setModaEdt,
  };
};
