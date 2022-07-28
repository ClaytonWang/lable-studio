import React, { useCallback } from 'react';
import { Table } from 'antd';
import { Elem } from '@/utils/bem';
import { Pagination } from '@/components';
import { useColumns } from './useColumns';
import { AddEditOrganization } from './AddEditOrganization';

export const OrganizationList = (props) => {
  const { data, currentPage, totalItems, pageSize, loadNextPage, loading } = props;
  const col = useColumns();

  const reload = useCallback((pageSize,fields) => {
    loadNextPage(1, pageSize,fields);
  }, []);

  const onClose = useCallback((force) => {
    if (force) reload();
    col.setModalAddEdit(null);
  },[]);

  return (
    <>
      <Elem name="list">
        <Table rowKey="id" columns={col.columns} dataSource={data} pagination={false} loading={loading} />
        {col.modalAddEdit && <AddEditOrganization onClose={ onClose} />}
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
