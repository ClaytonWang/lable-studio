import React, { useContext,useEffect,useState } from "react";
import { Table } from 'antd';
import { columns } from './Columns';
import { Elem } from '../../../utils/bem';
import { Pagination } from '../../../components';
import { SearchBar } from "./SearchBar";
import { ApiContext } from '../../../providers/ApiProvider';

const getCurrentPage = () => {
  const pageNumberFromURL = new URLSearchParams(location.search).get("page");

  return pageNumberFromURL ? parseInt(pageNumberFromURL) : 1;
};

export const ModelList = () => {
  const api = useContext(ApiContext);
  const [searchFields,setSearhFields] = useState();
  const [modelList, setmodelList] = React.useState([]);
  const [networkState, setNetworkState] = useState(null);
  const [currentPage, setCurrentPage] = useState(getCurrentPage());
  const [totalItems, setTotalItems] = useState(1);
  const defaultPageSize = parseInt(localStorage.getItem('pages:projects-list') ?? 10);

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

    setTotalItems(data?.count ?? 1);
    setmodelList(data.results ?? []);
    setNetworkState(false);
  };

  const loadNextPage = async (page, pageSize,searchFields) => {
    setCurrentPage(page);
    await fetchModelList(page, pageSize,searchFields);
  };

  const loadPage = (page, pageSize) => {
    loadNextPage(page, pageSize,searchFields);
  };

  useEffect(() => {
    fetchModelList();
  }, []);

  return (
    <>
      <Elem name="list">
        <SearchBar pageSize={defaultPageSize} onSearch={(pageSize,fields) => {
          setSearhFields(fields);
          loadNextPage(1, pageSize,fields);
        }} />
        <Table rowKey="id" columns={columns} dataSource={modelList} pagination={false} loading={ networkState} />
      </Elem>
      <Elem name="pages">
        <Pagination
          name="models-list"
          label="Models"
          page={currentPage}
          totalItems={totalItems}
          urlParamName="page"
          pageSize={defaultPageSize}
          pageSizeOptions={[10, 30, 50, 100]}
          onPageLoad={(page, pageSize) => loadPage(page, pageSize,searchFields)}
        />
      </Elem>
    </>
  );
};
