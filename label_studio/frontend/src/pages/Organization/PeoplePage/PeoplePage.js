import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { modal } from "../../../components/Modal/Modal";
import { Space } from "../../../components/Space/Space";
import { useAPI } from "../../../providers/ApiProvider";
import { Block, Elem } from "../../../utils/bem";
import "./PeopleInvitation.styl";
import { PeopleList } from "./PeopleList";
import "./PeoplePage.styl";
import { SelectedUser } from "./SelectedUser";
import { Button, Form ,Input,Select } from 'antd';
import { PlusOutlined } from '@ant-design/icons';

const layout = {
  labelCol: {
    span: 5,
  },
  wrapperCol: {
    span: 15,
  },
};

const groupName = (name) => {
  switch (name) {
    case 'admin':
      return '管理员';
    case 'user':
      return '普通用户';
  }
};

const InvitationModal = (props) => {
  const api = useAPI();
  const { roles,onClose } = props;
  const [waiting, setWaiting] = useState(false);

  const tailLayout = {
    wrapperCol: {
      offset: 4,
      span: 16,
    },
  };
  const onFinish = useCallback(async (values) => {
    setWaiting(true);
    await api.callApi("createUser",{
      body: values,
    });

    setWaiting(false);
    onClose(true);
  }, []);

  return (
    <Block name="invite">
      <Form
        style={{ marginTop: 20 }}
        {...layout}
        onFinish={onFinish}
        layout="horizontal"
        autoComplete="off"
        colon={false}>
        <Form.Item
          rules={[
            {
              required: true,
              message: '请选择权限',
            },
          ]}
          name="group"
          label="角色">
          <Select
            placeholder="请选择权限"
            options={roles?.map(v => {
              return { label: groupName(v.name), value: v.id, name: v.name };
            })}
          />
        </Form.Item>
        <Form.Item
          name="email"
          label="邮箱"
          rules={[
            {
              required: true,
              message: '请输入邮箱',
            },
            {
              type: 'email',
              message: '请输入正确的邮箱',
            },
          ]}>
          <Input placeholder="请输入邮箱" />
        </Form.Item>
        <Form.Item
          label="姓名"
          required={true}
          style={{
            marginBottom: 0,
          }}
        >
          <Form.Item
            name="last_name"
            rules={[
              {
                required: true,
                message: '请输入姓',
              },
            ]}
            style={{
              display: 'inline-block',
              width: 'calc(50% - 8px)',
            }}
          >
            <Input placeholder="请输入姓" />
          </Form.Item>
          <Form.Item
            name="first_name"
            rules={[
              {
                required: true,
                message: '请输入名',
              },
            ]}
            style={{
              display: 'inline-block',
              width: 'calc(50% - 8px)',
              margin: '0 8px',
            }}
          >
            <Input placeholder="请输入名" />
          </Form.Item>
        </Form.Item>

        <Form.Item
          name="password"
          label="密码"
          rules={[
            {
              required: true,
              message: '请输入密码',
            },
          ]}
        >
          <Input.Password placeholder="请输入密码" autoComplete="false" />
        </Form.Item>
        <Form.Item label=" " {...tailLayout}>
          <Space>
            <Button htmlType="button" onClick={() => { onClose();}}>
            取消
            </Button>
            <Button type="primary" htmlType="submit" loading={waiting}>
            提交
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Block>
  );
};


export const PeoplePage = () => {
  const api = useAPI();

  const inviteModal = useRef();
  const [selectedUser, setSelectedUser] = useState(null);
  const [roleList, setRoleList] = useState([]);

  const selectUser = useCallback((user) => {
    setSelectedUser(user);

    localStorage.setItem('selectedUser', user?.id);
  }, [setSelectedUser]);

  const inviteModalProps = useCallback((roles) => ({
    title: t("Invite people", "邀请加入"),
    style: { width: 600, height: 450 },
    closeOnClickOutside: false,
    body: () => (
      <InvitationModal roles={roles} onClose={closeInvitationModal} />
    ),
  }), []);

  const closeInvitationModal = useCallback((force) => {
    inviteModal.current?.close();
    if (force) {
      window.location.reload();
    }
  });

  const showInvitationModal = useCallback(() => {
    inviteModal.current = modal(inviteModalProps(roleList));
  }, [inviteModalProps, roleList]);

  const defaultSelected = useMemo(() => {
    return localStorage.getItem('selectedUser');
  }, []);

  useEffect(async () => {
    const data = await api.callApi("roleList");

    setRoleList(data?.group);
  }, []);

  useEffect(() => {
    inviteModal.current?.update(inviteModalProps(roleList));
  }, [roleList]);

  return (
    <Block name="people">
      <Elem name="controls">
        <Space spread>
          <Space></Space>
          <Space>
            <Button icon={<PlusOutlined />} type="primary" onClick={showInvitationModal}>
              {t("Add People", "添加用户")}
            </Button>
          </Space>
        </Space>
      </Elem>
      <Elem name="content">
        <PeopleList
          selectedUser={selectedUser}
          defaultSelected={defaultSelected}
          onSelect={(user) => selectUser(user)}
        />

        {selectedUser && (
          <SelectedUser
            user={selectedUser}
            onClose={() => selectUser(null)}
          />
        )}
      </Elem>
    </Block>
  );
};

PeoplePage.title = t("People");
PeoplePage.path = "/";
