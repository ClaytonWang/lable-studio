import React, { useContext, useEffect,useState } from 'react';
import { ModelList } from "./ModelPage/ModelList";
import { Button } from '../../components';
import { useContextProps } from '../../providers/RoutesProvider';
import { ModelImport } from "./ModelPage/ModelImport";
import { ModelExport } from "./ModelPage/ModelExport";
import { Block, Elem } from '../../utils/bem';
import { Oneof } from '../../components/Oneof/Oneof';
import { Loading } from '../../components';
import { ApiContext } from '../../providers/ApiProvider';

const getCurrentPage = () => {
  const pageNumberFromURL = new URLSearchParams(location.search).get("page");

  return pageNumberFromURL ? parseInt(pageNumberFromURL) : 1;
};

export const ModelManagerPage = () => {
  const api = useContext(ApiContext);
  const setContextProps = useContextProps();
  const [modelList, setmodelList] = React.useState([]);
  const [networkState, setNetworkState] = useState(null);
  const [currentPage, setCurrentPage] = useState(getCurrentPage());
  const [totalItems, setTotalItems] = useState(1);
  const [modal, setModal] = useState(false);
  const openModal = setModal.bind(null, true);
  const closeModal = setModal.bind(null, false);
  const defaultPageSize = parseInt(localStorage.getItem('pages:projects-list') ?? 30);

  const fetchModelList = async (page  = currentPage, pageSize = defaultPageSize) => {
    setNetworkState('loading');

    //need change
    // const data = await api.callApi("models", {
    //   params: { page, page_size: pageSize },
    // });

    const data = {
      count: 7,
      next: null,
      previous: null,
      results: [
        {},
      ],
    };

    await new Promise(resolve => setTimeout(resolve, 1000));

    setTotalItems(data?.count ?? 1);
    setmodelList(data.results ?? []);
    setNetworkState('loaded');
  };

  const loadNextPage = async (page, pageSize) => {
    setCurrentPage(page);
    await fetchModelList(page, pageSize);
  };

  React.useEffect(() => {
    fetchModelList();
  }, []);

  useEffect(() => {
    setContextProps({ openModal });
  }, []);

  return (
    <Block name="projects-page">
      <Oneof value={networkState}>
        <Elem name="loading" case="loading">
          <Loading size={64}/>
        </Elem>
      </Oneof>
      <Elem name="content" case="loaded">
        <ModelList
          modelList={modelList}
          currentPage={currentPage}
          totalItems={totalItems}
          loadNextPage={loadNextPage}
          pageSize={defaultPageSize} />
        { modal && <ModelImport onClose={closeModal} /> }
      </Elem>
    </Block>
  );
};

ModelManagerPage.title= t("Models Management");
ModelManagerPage.path="/model-manager";
ModelManagerPage.exact = true;

ModelManagerPage.context = ({ openModal }) => {
  return <Button onClick={openModal} look="primary" size="compact">{t("Import Model")}</Button>;
};
