FROM node:20-alpine

WORKDIR /workspace

COPY package.json /workspace/package.json
COPY tsconfig.base.json /workspace/tsconfig.base.json
COPY apps/web/package.json /workspace/apps/web/package.json
COPY packages/shared/package.json /workspace/packages/shared/package.json

RUN npm install

COPY apps/web /workspace/apps/web
COPY packages/shared /workspace/packages/shared

RUN npm --workspace apps/web run build

EXPOSE 3000

CMD ["npm", "--workspace", "apps/web", "run", "start"]

