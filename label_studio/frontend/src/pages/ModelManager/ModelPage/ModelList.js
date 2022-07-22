import React, { useState } from "react";
import { Table } from 'antd';
import { columns } from './Columns';
import { Elem } from '../../../utils/bem';
import { Pagination } from '../../../components';
import { SearchBar } from "./SearchBar";


export const ModelList = (props) => {
  const [searchFields,setSearhFields] = useState();
  const { data,currentPage,totalItems,pageSize,loadNextPage,loading } = props;

  return (
    <>
      <Elem name="list">
        <SearchBar pageSize={pageSize} onSearch={(pageSize,fields) => {
          setSearhFields(fields);
          loadNextPage(1, pageSize,fields);
        }} />
        <Table rowKey="id" columns={columns} dataSource={data} pagination={false} loading={ loading} />
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
          onPageLoad={(page, pageSize) => loadNextPage(page, pageSize,searchFields)}
        />
      </Elem>
    </>
  );
};
