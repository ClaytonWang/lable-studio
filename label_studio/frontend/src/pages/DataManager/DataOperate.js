import React from 'react';
import { template } from '../../utils/util';

const Button = (props) => {
  return <button className="dm-button dm-button_size_medium dm-button_look_primary" {...props} />;
};

const DialogIntentOperate = ({ actions }) => {
  return (
    <>
      <Button onClick={actions.clean}>{t("label_clean")}</Button>
      <Button onClick={actions.prediction}>{t("label_prediction")}</Button>
      <Button onClick={actions.prompt}>{t("label_prompt")}</Button>
    </>
  );
};

const ResponseGenerateOperate = () => {
  return (
    <>
      <Button>{t("label_prediction")}</Button>
      <Button>{t("label_prompt")}</Button>
    </>
  );
};

const DataOperate = ({ project, actions }) => {
  const projectClass = template.class(project);

  // 根据不同模版展示不同操作按钮
  switch (projectClass) {
    // 0. 意图标注
    case 'intent-classification-for-dialog':
      return  <DialogIntentOperate actions={actions} />;
    // 1. 对话生成
    case 'conversational-ai-response-generation':
      return  <ResponseGenerateOperate actions={actions} />;
    default:
      return null;
  }
};

export default DataOperate;