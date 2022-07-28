import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { LsPlus } from "../../../assets/icons";
import { Button } from "../../../components";
import { Description } from "../../../components/Description/Description";
import { Input } from "../../../components/Form";
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

const InvitationModal = ({ link }) => {
  return (
    <Block name="invite">
      <Input
        value={link}
        style={{ width: '100%' }}
        readOnly
      />

      <Description style={{ width: '70%', marginTop: 16 }}>
        {t("invite_description", "邀请加入的用户，拥有所有项目权限")}
        {/* Invite people to join your Label Studio instance. People that you invite have full access to all of your projects.  */}
        {/* <a href="https://labelstud.io/guide/signup.html">Learn more</a>. */}
      </Description>
    </Block>
  );
};

export const PeoplePage = () => {
  const api = useAPI();
  const history = useHistory();
  const inviteModal = useRef();
  const config = useConfig();
  const [selectedUser, setSelectedUser] = useState(null);

  const [link, setLink] = useState();

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

  useEffect(() => {
    api.callApi("inviteLink").then(({ invite_url }) => {
      setInviteLink(invite_url);
    });
  }, []);

  useEffect(() => {
    inviteModal.current?.update(inviteModalProps(link));
  }, [link]);

  const changeOrganization = () => {
    history.push('org-manage');
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
            <Button icon={<LsPlus/>} primary onClick={changeOrganization}>
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
