import { Space } from '../../../components/Space/Space';
import { Elem } from '../../../utils/bem';
import { Userpic } from '../../../components';
import { format } from 'date-fns';

export const columns = [
  {
    title: '模型名称',
    dataIndex: 'title',
    key: 'title',
    render: (text) => <a>{text}</a>,
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
    dataIndex: 'model',
    key: 'model',
    render: (_,record) => {
      if (!record.model) return '/';
      return record.model;
    },
  },
  {
    title: '项目集',
    dataIndex: 'project',
    key: 'project',
    render: (_,record) => {
      if (!record.project) return '/';
      return record.project;
    },
  },
  {
    title: '操作',
    dataIndex: 'action',
    key: 'action',
    render: (_, record) => (
      <Space size="middle">
        <a>编辑</a>
        <a>导出</a>
      </Space>
    ),
  },
];
