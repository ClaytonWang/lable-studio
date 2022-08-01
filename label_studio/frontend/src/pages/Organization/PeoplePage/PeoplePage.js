import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { LsPlus } from "../../../assets/icons";
import { Button } from "../../../components";
import { Input,Select } from "../../../components/Form";
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

const InvitationModal = ({ link }) => {
  const [form] = Form.useForm();

  return (
    <Block name="invite">
      <Form
        style={{ marginTop: 20 }}
        {...layout}
        form={form}
        initialValues={{ group_id: "2", organization_id: "1", code: "" ,url:"" }}
        layout="horizontal"
        name="form_in_org"
        colon={false}>
        <Form.Item
          name="group_id"
          label="角色">
          <div style={{ width: 250 }}>
            <Select
              options={[
                { label: "标注员", value: "3" },
                { label: "普通用户", value: "2" },
                { label: "管理员", value: "1" },
              ]}
            />
          </div>
        </Form.Item>
        <Form.Item
          name="organization_id"
          label="组织">
          <div style={{ width: 250 }}>
            <Select
              options={[
                { label: "上海移动大数据中心", value: "1" },
                { label: "普通用户", value: "2" },
                { label: "管理员", value: "3" },
              ]}
            />
          </div>
        </Form.Item>
        <Form.Item
          name="code"
          label="注册验证码"
        >
          <Input style={{ width: 250 }} />
          {/* <Button >复制验证码</Button> */}
        </Form.Item>
        <Form.Item
          name="code"
          label="注册链接"
        >
          <Input style={{ width: 350 }} value={link} readOnly />
          {/* <Button >复制验链接</Button> */}
        </Form.Item>
      </Form>
    </Block>
  );
};

const createCode = ()=> {
  let code = "";
  var codeLength = 6;//验证码的长度，可变
  var selectChar = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];//所有候选组成验证码的字符

  for (var i = 0; i < codeLength; i++) {
    var charIndex = Math.floor(Math.random() * 36);

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


  const selectUser = useCallback((user) => {
    setSelectedUser(user);

    localStorage.setItem('selectedUser', user?.id);
  }, [setSelectedUser]);

  const setInviteLink = useCallback((link) => {
    const hostname = config.hostname || location.origin;

    setLink(`${hostname}${link}`);
  }, [config, setLink]);

  const updateLink = useCallback(() => {
    api.callApi('resetInviteLink').then(({ invite_url }) => {
      setInviteLink(invite_url);
    });
  }, [setInviteLink]);

  const inviteModalProps = useCallback((link) => ({
    title: t("Invite people", "邀请加入"),
    style: { width: 640, height: 472 },
    body: () => (
      <InvitationModal link={link}/>
    ),
    footer: () => {
      const [copied, setCopied] = useState(false);

      const copyLink = useCallback(() => {
        setCopied(true);
        copyText(link);
        setTimeout(() => setCopied(false), 1500);
      }, []);

      return (
        <Space spread>
          <Space>
            <Button style={{ width: 170 }} onClick={() => updateLink()}>
              {t("Reset Link")}
            </Button>
          </Space>
          <Space>
            <Button primary style={{ width: 170 }} onClick={copyLink}>
              {copied ? t("Copied!", "已复制！") : t("Copy link", "复制链接")}
            </Button>
          </Space>
        </Space>
      );
    },
    bareFooter: true,
  }), []);

  const showInvitationModal = useCallback(() => {
    inviteModal.current = modal(inviteModalProps(link));
  }, [inviteModalProps, link]);

  const defaultSelected = useMemo(() => {
    return localStorage.getItem('selectedUser');
  }, []);

  useEffect(async () => {

    const groups = await api.callApi("roleList");

    setRoleList(groups);

    api.callApi("signInvite", {
      body: {
        code: validateCode,
        group_id: "",
        organization_id:config.user.orgnazition.id,
      } }).then(({ invite_url }) => {
      setInviteLink(invite_url);
    });
  }, []);

  useEffect(() => {
    inviteModal.current?.update(inviteModalProps(link));
  }, [link]);

  const changeOrganization = () => {
    history.push('organization/list');
  };

  return (
    <Block name="people">
      <Elem name="controls">
        <Space spread>
          <Space></Space>

          <Space>
            <Button icon={<LsPlus/>} primary onClick={showInvitationModal}>
              {t("Add People", "添加用户")}
            </Button>
            <Button icon={<SwapOutlined rotate={ 90} />} primary onClick={changeOrganization}>
              {t("Change Organization", "切换组织")}
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
