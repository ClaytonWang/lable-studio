import React from 'react';

import { Button } from "../../components";
import { Elem } from "../../components/Menu/MenuContext";
import { modal } from "../../components/Modal/Modal";
import { useModalControls } from "../../components/Modal/ModalPopup";
import { Space } from "../../components/Space/Space";
import { useAPI } from "../../providers/ApiProvider";
import { Block, cn } from "../../utils/bem";



export const WebhookDeleteModal = ({ onDelete }) => {
  return modal({
    title: t("Delete"),
    body: ()=>{
      const ctrl = useModalControls();
      const rootClass = cn('webhook-delete-modal');

      return (
        <div className={rootClass}>
          <div className={rootClass.elem('modal-text')}>
            {t('tip_cannot_undone')}
            {/* Are you sure you want to delete the webhook? This action */}
            {/* cannot be undone.   */}
          </div>

        </div>
      );},
    footer: ()=>{
      const ctrl = useModalControls();
      const rootClass = cn('webhook-delete-modal');

      return (
        <Space align="end">
          <Button 
            className={rootClass.elem('width-button')} 
            onClick={()=>{ctrl.hide();}}>
            {t('Cancel')}
          </Button>
          <Button 
            look="destructive"
            className={rootClass.elem('width-button')}
            onClick={
              async ()=>{
                await onDelete();
                ctrl.hide();
              }
            }
          >{t('Delete')}</Button>
        </Space>
      );
    },
    style: { width: 512 },
  });
};