import { Button } from "@/components";
import React, { useCallback,useContext,useEffect,useState } from 'react';
import { useContextProps } from '@/providers/RoutesProvider';
import { Block, Elem } from '@/utils/bem';
import { ApiContext } from '@/providers/ApiProvider';
import { Space } from "@/components/Space/Space";
import { AddEditOrganization } from './AddEditOrganization';
import { OrganizationList } from './OrganizationList';
import { useHistory } from "react-router";
import { LsPlus } from "@/assets/icons";

const getCurrentPage = () => {
  const pageNumberFromURL = new URLSearchParams(location.search).get("page");

  return pageNumberFromURL ? parseInt(pageNumberFromURL) : 1;
};

const OrgManager = () => {
  const api = useContext(ApiContext);
  const history = useHistory();
  const [modal, setModal] = useState(false);
  const openModal = setModal.bind(null, true);
  const closeModal = setModal.bind(null, false);
  const setContextProps = useContextProps();
  const [totalItems, setTotalItems] = useState(1);
  const [dataList, setDataList] = React.useState([]);
  const [networkState, setNetworkState] = useState(null);
  const [currentPage, setCurrentPage] = useState(getCurrentPage());
  const defaultPageSize = parseInt(localStorage.getItem('pages:org-list') ?? 10);

  const fetchList = async (
    page = currentPage,
    pageSize = defaultPageSize,
  ) => {
    setNetworkState(true);
    const data = await api.callApi("orgList", {
      params: {
        page,
        page_size: pageSize,
      },
    });

    setTotalItems(data?.count ?? 1);
    setDataList(data ?? []);
    setNetworkState(false);
  };

  const loadNextPage = async (page, pageSize) => {
    setCurrentPage(page);
    await fetchList(page, pageSize);
  };

  const gotoOrg = () => {
    history.replace('/organization');
  };

  const onClose = useCallback((force) => {
    if(force) fetchList();
    closeModal();
  },[]);


  useEffect(() => {
    fetchList();
    setContextProps({ openModal ,gotoOrg });
  }, []);

  return (
    <Block name="organization-page">
      <Elem name="content" case="loaded">
        <OrganizationList
          loading={networkState}
          data={dataList}
          currentPage={currentPage}
          totalItems={totalItems}
          loadNextPage={loadNextPage}
          pageSize={defaultPageSize} />
        {modal && <AddEditOrganization onClose={ onClose} />}
      </Elem>
    </Block>
  );
};

OrgManager.context = ({ openModal,gotoOrg }) => {
  return (
    <Space>
      <Button onClick={gotoOrg} size="compact">
        返回
      </Button>
      <Button icon={<LsPlus/>} onClick={openModal} look="primary" size="compact">
        新增组织
      </Button>
    </Space>
  );
};

export const OrgManagerPage = {
  title: t('org-list','组织列表'),
  path: "/list",
  component: OrgManager,
};
