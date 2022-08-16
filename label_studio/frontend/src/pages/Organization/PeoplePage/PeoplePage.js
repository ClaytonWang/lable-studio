import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { LsPlus } from "../../../assets/icons";
import { Button } from "../../../components";
import { Input, Select } from "../../../components/Form";
import { modal } from "../../../components/Modal/Modal";
import { Space } from "../../../components/Space/Space";
import { useAPI } from "../../../providers/ApiProvider";
import { useConfig } from "../../../providers/ConfigProvider";
import { Block, Elem } from "../../../utils/bem";
import { copyText } from "../../../utils/helpers";
import "./PeopleInvitation.styl";
import { PeopleList } from "./PeopleList";
import "./PeoplePage.styl";
import { SelectedUser } from "./SelectedUser";
import { useHistory } from 'react-router';
import { SwapOutlined } from '@ant-design/icons';
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
    case 'annotator':
      return '标注员';
  }
};

const InvitationModal = (props) => {
  const config = useConfig();
  const [copiedCode, setCopiedCode] = useState(false);
  const [copiedLink, setCopiedLink] = useState(false);
  const [form] = Form.useForm();
  const { link, roles, orgs, code, roleId, orgId, onUpdate ,inviteId } = props;
  const copyTxt = useCallback((txt, type) => {
    if (type === 'code')
      setCopiedCode(true);
    else
      setCopiedLink(true);

    copyText(txt);
    if (type === 'code')
      setTimeout(() => setCopiedCode(false), 2000);
    else
      setTimeout(() => setCopiedLink(false), 2000);

  }, []);

  return (
    <Block name="invite">
      <Form
        style={{ marginTop: 20 }}
        {...layout}
        form={form}
        initialValues={{ group_id: roleId, organization_id: orgId, code, link }}
        layout="horizontal"
        name="form_in_org"
        colon={false}>
        <Form.Item
          name="group_id"
          label="角色">
          <div style={{ width: 250 }}>
            <Select
              value={roleId}
              options={roles?.map(v => {
                return { label: groupName(v.name), value: v.id, name: v.name };
              })}
              onChange={(e) => {
                form.setFieldsValue({ group_id: e.target.value });
                let organization_id = form.getFieldValue('organization_id');

                if (!organization_id) {
                  organization_id = config.user.orgnazition.id;
                }

                onUpdate({
                  inviteId,
                  code,
                  group_id: e.target.value,
                  organization_id,
                });
              }}
            />
          </div>
        </Form.Item>
        <Form.Item
          name="organization_id"
          label="组织">
          <div style={{ width: 250 }}>
            <Select
              value={orgId}
              options={orgs?.map(v => {
                return { label: v.title, value: v.id };
              })}
              onChange={(e) => {
                form.setFieldsValue({ organization_id: e.target.value });
                let group_id = form.getFieldValue('group_id');

                if (!group_id) {
                  [{ id: group_id }] = roles?.filter((v) => { return v.name === 'user'; });
                }
                onUpdate({
                  inviteId,
                  code,
                  group_id,
                  organization_id: e.target.value,
                });
              }}
            />
          </div>
        </Form.Item>
        <Form.Item
          name="code"
          label="注册验证码"
        >
          <>
            <Input style={{ width: 250 }} value={code} readOnly />
            <Button primary onClick={() => { copyTxt(code, 'code'); }} >
              {copiedCode ? t("Copied!", "已复制！") : '复制验证码'}</Button>
          </>
        </Form.Item>
        <Form.Item
          name="link"
          label="注册链接"
        >
          <>
            <Input style={{ width: 330 }} value={link} readOnly />
            <Button primary onClick={() => { copyTxt(link, 'link'); }}>
              {copiedLink ? t("Copied!", "已复制！") : t("Copy link", "复制链接")}</Button>
          </>
        </Form.Item>
      </Form>
    </Block>
  );
};

const createCode = () => {
  let code = "";
  var codeLength = 6;//验证码的长度，可变
  var selectChar = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];//所有候选组成验证码的字符

  for (var i = 0; i < codeLength; i++) {
    var charIndex = Math.floor(Math.random() * 10);

    code += selectChar[charIndex];
  }
  return code;
};

export const PeoplePage = () => {
  const api = useAPI();
  const history = useHistory();
  const inviteModal = useRef();
  const config = useConfig();
  const [selectedUser, setSelectedUser] = useState(null);

  const [link, setLink] = useState();
  const [roleList, setRoleList] = useState([]);
  const [orgList, setOrgList] = useState([]);
  const [validateCode, setValidateCode] = useState(createCode());
  const [roleId, setRoleId] = useState();
  const [orgId, setOrgId] = useState();
  const [inviteId, setInviteId] = useState();

  const selectUser = useCallback((user) => {
    setSelectedUser(user);

    localStorage.setItem('selectedUser', user?.id);
  }, [setSelectedUser]);

  const setInviteLink = useCallback(() => {
    const hostname = config.hostname || location.origin;

    setLink(`${hostname}${'/user/signup'}`);
  }, [config, setLink]);

  const updateInviteCode = (values) => {
    api.callApi("updateInvite", {
      params: {
        pk: values.inviteId,
      },
      body: values,
    });
  };

  const updateLink = useCallback((values) => {
    values.code = createCode();
    if (values.inviteId) {
      updateInviteCode(values);
    } else {
      api.callApi("signInvite", { body: values, errorFilter: () => true }).then((data) => {
        if (data?.status === 400) {
          //code duplicated
          values.code = createCode();
          api.callApi("signInvite", { body: values, errorFilter: () => true }).then((rsp) => {
            if (rsp.status === 400) {
              console.log(rsp);
            } else {
              setInviteId(rsp?.id);
            }
          });
        } else {
          setInviteId(data?.id);
        }
      });
    }

    setValidateCode(values.code);
    setOrgId(values.organization_id);
    setRoleId(values.group_id);
  }, [setInviteLink]);

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
        inviteId={inviteId}
        onUpdate={updateLink} />
    ),
  }), []);

  const showInvitationModal = useCallback(() => {
    const [{ id: group_id }] = roleList?.filter((v) => { return v.name === 'user'; });

    updateLink({ group_id, organization_id: config.user.orgnazition.id });
    inviteModal.current = modal(inviteModalProps(link, roleList, orgList, validateCode, roleId, orgId, inviteId));
  }, [inviteModalProps, link, roleList, orgList, validateCode, roleId, orgId,inviteId]);

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
    inviteModal.current?.update(inviteModalProps(link, roleList, orgList, validateCode, roleId, orgId,inviteId));
  }, [link, roleList, orgList, validateCode, roleId, orgId,inviteId]);

  const changeOrganization = () => {
    history.push('organization/list');
  };

  return (
    <Block name="people">
      <Elem name="controls">
        <Space spread>
          <Space></Space>

          <Space>
            <Button icon={<LsPlus />} primary onClick={showInvitationModal}>
              {t("Add People", "添加用户")}
            </Button>
            {
              !Object.keys(config.user.button).includes("001") && (
                <Button icon={<SwapOutlined rotate={90} />} primary onClick={changeOrganization}>
                  {t("Change Organization", "切换组织")}
                </Button>
              )
            }
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
