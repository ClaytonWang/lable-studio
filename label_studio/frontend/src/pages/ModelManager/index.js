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
import "./index.styl";

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

    const data = await api.callApi("modelManager", {
      params: {
        page,
        page_size: pageSize,
        type: 'intention',
        version: 'v1.0',
        mdoel_group: '',
        project_group:'',
      },
    });

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
    <Block name="models-page">
      <Oneof value={networkState}>
        <Elem name="loading" case="loading">
          <Loading size={64}/>
        </Elem>
        <Elem name="content" case="loaded">
          <ModelList
            modelList={modelList}
            currentPage={currentPage}
            totalItems={totalItems}
            loadNextPage={loadNextPage}
            pageSize={defaultPageSize} />
          { modal && <ModelImport onClose={closeModal} /> }
        </Elem>
      </Oneof>
    </Block>
  );
};

ModelManagerPage.title= t("Models Management");
ModelManagerPage.path="/model-manager";
ModelManagerPage.exact = true;

ModelManagerPage.context = ({ openModal }) => {
  return <Button onClick={openModal} look="primary" size="compact">{t("Import Model")}</Button>;
};
