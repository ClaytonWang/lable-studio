import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { LsPlus } from "../../../assets/icons";
import { Button } from "../../../components";
import { Input, Select } from "../../../components/Form";
import { modal } from "../../../components/Modal/Modal";
import { Space } from "../../../components/Space/Space";
import { useAPI } from "../../../providers/ApiProvider";
import { useConfig } from "../../../providers/ConfigProvider";
import { Block, Elem } from "../../../utils/bem";
import "./PeopleInvitation.styl";
import { PeopleList } from "./PeopleList";
import "./PeoplePage.styl";
import { SelectedUser } from "./SelectedUser";
import { Form } from 'antd';

const layout = {
  labelCol: {
    span: 5,
  },
  wrapperCol: {
    span: 19,
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
  const [form] = Form.useForm();
  const { link, roles, roleId } = props;

  return (
    <Block name="invite">
      <Form
        style={{ marginTop: 20 }}
        {...layout}
        form={form}
        initialValues={{ group_id: roleId, link }}
        layout="horizontal"
        name="form_in_org"
        colon={false}>
        <Form.Item
          name="role"
          label="角色">
          <div style={{ width: 150 }}>
            <Select
              options={roles?.map(v => {
                return { label: groupName(v.name), value: v.id, name: v.name };
              })}
              onChange={(e) => {
                form.setFieldsValue({ role: e.target.value });
              }}
            />
          </div>
        </Form.Item>
        <Form.Item
          name="email"
          label="邮箱">
          <div style={{ width: 350 }}>
            <Input />
          </div>
        </Form.Item>
        <Form.Item
          label="姓名"
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
              width: 'calc(50% - 38px)',
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
              width: 'calc(50% - 50px)',
              margin: '0 38px',
            }}
          >
            <Input placeholder="请输入名" />
          </Form.Item>
        </Form.Item>

        <Form.Item
          name="password"
          label="密码"
        >
          <div style={{ width: 350 }} >
            <Input />
          </div>
        </Form.Item>
      </Form>
    </Block>
  );
};


export const PeoplePage = () => {
  const api = useAPI();

  const inviteModal = useRef();
  const config = useConfig();
  const [selectedUser, setSelectedUser] = useState(null);
  const [link, setLink] = useState();
  const [roleList, setRoleList] = useState([]);
  const [orgList, setOrgList] = useState([]);

  const selectUser = useCallback((user) => {
    setSelectedUser(user);

    localStorage.setItem('selectedUser', user?.id);
  }, [setSelectedUser]);

  const setInviteLink = useCallback(() => {
    const hostname = config.hostname || location.origin;

    setLink(`${hostname}${'/user/signup'}`);
  }, [config, setLink]);

  const inviteModalProps = useCallback((link, roles, orgs, code, roleId, orgId, inviteId) => ({
    title: t("Invite people", "邀请加入"),
    style: { width: 640, height: 472 },
    body: () => (
      <InvitationModal
        link={link}
        roles={roles}
        orgs={orgs}
        code={code}
        roleId={roleId}
        orgId={orgId}
        inviteId={inviteId} />
    ),
  }), []);

  const showInvitationModal = useCallback(() => {
    const [{ id: role }] = roleList?.filter((v) => { return v.name === 'user'; });

    inviteModal.current = modal(inviteModalProps(link, roleList, orgList));
  }, [inviteModalProps, link, roleList, orgList]);

  const defaultSelected = useMemo(() => {
    return localStorage.getItem('selectedUser');
  }, []);

  useEffect(async () => {

    const data = await api.callApi("roleList");

    setRoleList(data?.group);
    setOrgList(data?.organization);
    setInviteLink();

  }, []);

  useEffect(() => {
    inviteModal.current?.update(inviteModalProps(link, roleList, orgList, roleId, orgId,inviteId));
  }, [link, roleList, orgList, roleId, orgId,inviteId]);

  return (
    <Block name="people">
      <Elem name="controls">
        <Space spread>
          <Space></Space>

          <Space>
            <Button icon={<LsPlus />} primary onClick={showInvitationModal}>
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
