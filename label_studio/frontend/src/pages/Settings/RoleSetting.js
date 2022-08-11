import { useCallback, useContext, useEffect, useState } from 'react';
import { Button, Checkbox, Pagination, Spinner, Userpic } from "@/components";
import { useAPI } from "@/providers/ApiProvider";
import { Label } from '@/components/Form';
import { usePage, usePageSize } from "@/components/Pagination/Pagination";
import { Block, Elem } from "@/utils/bem";
import { CopyableTooltip } from '@/components/CopyableTooltip/CopyableTooltip';
import { ProjectContext } from '../../providers/ProjectProvider';

export const RoleSetting = () => {
  const api = useAPI();
  const [usersList, setUsersList] = useState();
  const [currentPage] = usePage('page', 1);
  const [currentPageSize] = usePageSize('page_size', 30);
  const [totalItems, setTotalItems] = useState(0);
  const { project } = useContext(ProjectContext);

  const fetchUsers = useCallback(async (page, pageSize) => {
    const response = await api.callApi('usersList', {
      params: {
        group: 'annotator',
        page,
        page_size: pageSize,
      },
    });

    if (response) {
      response.map((user) => {
        user.hasRole = user.project_ids.includes(project.id);
        return user;
      });
      setUsersList(response);
      setTotalItems(response.length);
    }
  }, [api]);

  const setRole = useCallback((user_id) => {
    const list = usersList.map(u => {
      if (u.id === user_id) {
        const tmp = { ...u };
        const index = tmp.project_ids.indexOf(project.id);

        if (index >= 0) {
          tmp.project_ids.splice(index, 1);
          tmp.hasRole = false;
        } else {
          tmp.project_ids.push(project.id);
          tmp.hasRole = true;
        }
        return tmp;
      }
      return u;
    });

    setUsersList(list);
  }, [usersList]);

  const saveConfig = useCallback(async () => {
    const ids = [];

    usersList?.forEach((v) => {
      if (v.hasRole) {
        ids.push(v.id);
      }
    });

    await api.callApi('addProjectRole', {
      params: {
        pk: project.id,
      },
      body: {
        user_ids: ids.join(","),
      },
    });
  }, [usersList]);

  useEffect(() => {
    fetchUsers(currentPage, currentPageSize);
  }, []);

  return (
    <>
      <Block name="people-list">
        <Label text={"选择可见的标注员"} large />
        <div style={{ color: "rgba(0,0,0,0.4)", paddingLeft: 16 }}>
          该文件对组织内其他角色均可见,仅支持调整标注员可见范围
        </div>
        <Elem name="wrapper" style={{ marginLeft: 16 }}>
          {usersList ? (
            <Elem name="users">
              <Elem name="header">
                <Elem name="column" mix="checkbox" style={{ with: 28 }} />
                <Elem name="column" mix="avatar" />
                <Elem name="column" mix="email">{t("Email")}</Elem>
                <Elem name="column" mix="name">{t("Name")}</Elem>
              </Elem>
              <Elem name="body">
                {usersList.map((user) => {
                  return (
                    <Elem key={`user-${user.id}`} name="user" >
                      <Elem name="field" mix="checkbox">
                        <Checkbox checked={user.hasRole} onChange={() => { setRole(user.id); }} />
                      </Elem>
                      <Elem name="field" mix="avatar">
                        <CopyableTooltip title={'User ID: ' + user.id} textForCopy={user.id}>
                          <Userpic user={user} style={{ width: 28, height: 28 }} />
                        </CopyableTooltip>
                      </Elem>
                      <Elem name="field" mix="email">
                        {user.email}
                      </Elem>
                      <Elem name="field" mix="name">
                        {user.last_name}{user.first_name}
                      </Elem>
                    </Elem>
                  );
                })}
              </Elem>
            </Elem>
          ) : (
            <Elem name="loading">
              <Spinner size={36} />
            </Elem>
          )}
        </Elem>
        <Button look="primary" style={{ float: 'right', width: 100, marginTop: 20 }} onClick={saveConfig}>{t("Save")}</Button>
        <Pagination
          page={currentPage}
          urlParamName="page"
          totalItems={totalItems}
          pageSize={currentPageSize}
          pageSizeOptions={[30, 50, 100]}
          onPageLoad={fetchUsers}
          style={{ paddingTop: 16 }}
        />
      </Block>
    </>
  );
};

RoleSetting.title = '可见范围';
RoleSetting.path = "/role";
