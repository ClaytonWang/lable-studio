import React from "react";
import { Table } from 'antd';
import { columns } from './Columns';
import { Elem } from '../../../utils/bem';
import { Pagination } from '../../../components';
import { SearchBar } from "./SearchBar";

export const ModelList = (props) => {
  const { modelList,currentPage,totalItems,loadNextPage,pageSize } = props;

  return (
    <>
      <Elem name="list">
        <SearchBar />
        <Table rowKey="id" columns={columns} dataSource={modelList} pagination={false} />
      </Elem>
      <Elem name="pages">
        <Pagination
          name="models-list"
          label="Models"
          page={currentPage}
          totalItems={totalItems}
          urlParamName="page"
          pageSize={pageSize}
          pageSizeOptions={[10, 30, 50, 100]}
          onPageLoad={(page, pageSize) => loadNextPage(page, pageSize)}
        />
      </Elem>
    </>
  );
};
