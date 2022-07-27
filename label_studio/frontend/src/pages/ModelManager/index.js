import React, { useContext, useEffect,useState } from 'react';
import { ModelList } from "./ModelPage/ModelList";
import { Button } from '../../components';
import { useContextProps } from '../../providers/RoutesProvider';
import { ModelImport } from "./ModelPage/ModelImport";
import { Block, Elem } from '../../utils/bem';
import { CloudUploadOutlined } from '@ant-design/icons';
import { ApiContext } from '../../providers/ApiProvider';
import "./index.styl";

const getCurrentPage = () => {
  const pageNumberFromURL = new URLSearchParams(location.search).get("page");

  return pageNumberFromURL ? parseInt(pageNumberFromURL) : 1;
};

export const ModelManagerPage = () => {
  const api = useContext(ApiContext);
  const setContextProps = useContextProps();
  const [totalItems, setTotalItems] = useState(1);
  const [modelList, setmodelList] = React.useState([]);
  const [networkState, setNetworkState] = useState(null);
  const [modal, setModal] = useState(false);
  const openModal = setModal.bind(null, true);
  const closeModal = setModal.bind(null, false);
  const defaultPageSize = parseInt(localStorage.getItem('pages:projects-list') ?? 10);
  const [currentPage, setCurrentPage] = useState(getCurrentPage());

  const fetchModelList = async (
    page = currentPage,
    pageSize = defaultPageSize,
    searchFields,
  ) => {
    setNetworkState(true);
    const data = await api.callApi("modelManager", {
      params: {
        page,
        page_size: pageSize,
        ...searchFields,
      },
    });

    const results = data.results.map(v => {
      v.model = v.model ?? '';
      v.project = v.project ?? '';
      return v;
    });

    setTotalItems(data?.count ?? 1);
    setmodelList(results ?? []);
    setNetworkState(false);
  };

  const loadNextPage = async (page, pageSize,searchFields) => {
    setCurrentPage(page);
    await fetchModelList(page, pageSize,searchFields);
  };

  useEffect(() => {
    fetchModelList();
    setContextProps({ openModal });
  }, []);

  return (
    <Block name="models-page">
      <Elem name="content" case="loaded">
        <ModelList
          loading={ networkState}
          data={modelList}
          currentPage={currentPage}
          totalItems={totalItems}
          loadNextPage={loadNextPage}
          pageSize={defaultPageSize} />
        {modal && (
          <ModelImport onClose={(force) => {
            if (force) {
              fetchModelList();
            }
            closeModal();
          }} />
        ) }
      </Elem>
    </Block>
  );
};

ModelManagerPage.title= t("Models Management");
ModelManagerPage.path="/model-manager";
ModelManagerPage.exact = true;

ModelManagerPage.context = ({ openModal }) => {
  return <Button onClick={openModal} look="primary" size="compact" icon={<CloudUploadOutlined style={{ width:20,height:20,marginLeft:-10 }} />}>{t("Import Model")}</Button>;
};
