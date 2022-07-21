import React, { useCallback, useState } from 'react';
import { Modal } from '../../../components/Modal/Modal';
import { cn } from '../../../utils/bem';

export const ModelImport = ({ onClose }) => {
  const rootClass = cn("create-project");

  const onHide = useCallback(async () => {

    history.replace("/model-configer");
    onClose?.();
  }, []);

  return (
    <Modal style={{ width: 500 }} o
      nHide={onHide} visible
      closeOnClickOutside={false}
      allowClose={true}
      title={t("Import Model")}
    >
      <div className={rootClass}>
      </div>
    </Modal>
  );
};
