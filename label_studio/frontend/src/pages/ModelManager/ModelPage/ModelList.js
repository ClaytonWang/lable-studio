import React, { useCallback, useState } from "react";
import { Table } from 'antd';
import { useColumns } from './useColumns';
import { Elem } from '../../../utils/bem';
import { Pagination } from '../../../components';
import { SearchBar } from "./SearchBar";
import { ModelExport } from './ModelExport';
import { ModelEdit } from "./ModelEdit";


export const ModelList = (props) => {
  const [searchFields, setSearhFields] = useState();
  const { data, currentPage, totalItems, pageSize, loadNextPage, loading } = props;
  const col = useColumns();

  const reload = useCallback((pageSize, fields) => {
    loadNextPage(1, pageSize, fields);
  }, []);

  const onSearch = useCallback((pageSize, fields) => {
    setSearhFields(fields);
    reload(pageSize, fields);
  }, []);

  const onClose = useCallback((force, type) => {
    if (force) reload();
    if (type === 'export')
      col.setModalExp(null);
    else if (type === 'edit')
      col.setModaEdt(null);
  }, []);

  return (
    <>
      <Elem name="list">
        <SearchBar pageSize={pageSize} onSearch={onSearch} />
        <Table rowKey="id" columns={col.columns} dataSource={data} pagination={false} loading={loading} />
        {col.modalExp ? (
          <ModelExport data={col.modalExp} onClose={onClose} />
        ) : null}
        {col.modalEdt ? (
          <ModelEdit data={col.modalEdt} onClose={onClose} />
        ) : null}
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
          onPageLoad={(page, pageSize) => loadNextPage(page, pageSize, searchFields)}
        />
      </Elem>
    </>
  );
};
