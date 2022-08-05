import { Space } from '../../../components/Space/Space';
import { Elem } from '../../../utils/bem';
import { Userpic } from '../../../components';
import { format } from 'date-fns';
import { useMemo, useState } from 'react';


export const useColumns = () => {
  const [modalExp, setModalExp] = useState(null);
  const [modalEdt, setModaEdt] = useState(null);

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
                { _ }
              </Elem>
            );
          else
            return (<a>{record.title}</a>);
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
              <Userpic src="#" user={record.created_by} showUsername/>
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
              { record.version }
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
              { t(record.type) }
            </Elem>
          );
        },
      },
      {
        title: '模型集',
        dataIndex: 'title',
        key: 'title',
        render: (_,record) => {
          if (!record.title) return '/';
          return record.title;
        },
      },
      {
        title: '项目集合',
        dataIndex: 'project_set',
        key: 'project_set',
        render: (_,record) => {
          if (!record.project_set) return '/';
          return record.project_set?.title;
        },
      },
      {
        title: '操作',
        dataIndex: 'action',
        key: 'action',
        render: (_, record) => (
          <Space size="middle">
            <a onClick={() => { setModaEdt(record);}}>编辑</a>
            <a onClick={() => { setModalExp(record);}}>导出</a>
          </Space>
        ),
      },
    ];
  },[]);

  return {
    columns,
    modalExp,
    setModalExp,
    modalEdt,
    setModaEdt,
  };
};
